from __future__ import print_function
import numpy as np
import copy
import sys
from scipy.special import jv  # Bessel functions

# Import the original tb_model from the provided pythtb.txt structure
# Assuming pythtb.txt is saved as pythtb.py or content is pasted above.
# Here we assume the user puts this script in the same directory as pythtb.py
try:
    import pythtb
    from pythtb import tb_model
except ImportError:
    print("Error: Could not import 'tb_model' from 'pythtb'.")
    print("Please ensure pythtb.py is in the same directory.")
    sys.exit(1)

# Check pythtb version - must be 1.8.0
REQUIRED_PYTHTB_VERSION = "1.8.0"
pythtb_version = getattr(pythtb, '__version__', None)
if pythtb_version is None:
    raise RuntimeError(
        f"Could not determine pythtb version. "
        f"FloquetTB requires pythtb version {REQUIRED_PYTHTB_VERSION}. "
        f"Please ensure you have pythtb version {REQUIRED_PYTHTB_VERSION} installed."
    )
if pythtb_version != REQUIRED_PYTHTB_VERSION:
    raise RuntimeError(
        f"FloquetTB requires pythtb version {REQUIRED_PYTHTB_VERSION}, "
        f"but found version {pythtb_version}. "
        f"Please install pythtb version {REQUIRED_PYTHTB_VERSION}."
    )

class FloquetTB(tb_model):
    r"""
    A class to calculate the effective Floquet Hamiltonian for a periodically 
    driven tight-binding model using High-Frequency Expansion.

    It inherits from pythtb.tb_model.

    Parameters for initialization:
    :param bare_model: The static (undriven) pythtb.tb_model instance.
    """

    def __init__(self, bare_model):
        # Initialize the parent class with dimensions from the bare model
        super(FloquetTB, self).__init__(
            bare_model._dim_k,
            bare_model._dim_r,
            bare_model._lat,
            bare_model._orb,
            bare_model._per,
            bare_model._nspin
        )
        
        # Store original model data to allow re-calculation with different fields
        self._bare_hoppings = copy.deepcopy(bare_model._hoppings)
        self._bare_site_energies = copy.deepcopy(bare_model._site_energies)
        self._bare_model = bare_model


    def compute_floquet_hamiltonian(self, A, omega, polarization='circular_left', order=1):
        r"""
        Computes the effective Floquet Hamiltonian.
        """
        
        # Clear current model's Hamiltonian terms
        self._hoppings = []
        if self._nspin == 1:
            self._site_energies = np.zeros((self._norb), dtype=float)
        else:
            self._site_energies = np.zeros((self._norb, 2, 2), dtype=complex)
            
        # Direction factor for polarization chirality
        if polarization == 'circular_left':
            sigma = 1.0
        elif polarization == 'circular_right':
            sigma = -1.0
        else:
            raise NotImplementedError("Only circular polarization is supported.")

        # List to explicitly store the FULL H_1 operator (both i->j and j->i)
        # Structure: (amplitude, start_node, end_node, R_vector)
        H1_ops = []

        # Process all original hoppings
        for hop in self._bare_hoppings:
            bare_amp = hop[0]
            ind_i = hop[1]
            ind_j = hop[2]
            ind_R = np.array(hop[3]) if self._dim_k > 0 else np.zeros(self._dim_r)

            # --- Geometry Calculation ---
            pos_i = np.dot(self._orb[ind_i], self._lat)
            pos_j = np.dot(self._orb[ind_j], self._lat) + np.dot(ind_R, self._lat)
            d_vec = pos_j - pos_i # Vector from i to j
            d_len = np.linalg.norm(d_vec[:2]) 
            
            # --- 0th Order: Renormalization ---
            # Even for onsite/vertical hoppings (d_len=0), J0(0)=1, so logic holds.
            if d_len < 1e-6:
                # Onsite term (no phase modification usually)
                if ind_i == ind_j and np.allclose(ind_R, 0):
                     self._add_onsite_matrix(ind_i, bare_amp)
                else:
                    self.set_hop(bare_amp, ind_i, ind_j, ind_R, mode="add", allow_conjugate_pair=True)
                continue

            # Azimuthal angle phi
            phi = np.arctan2(d_vec[1], d_vec[0])
            z_arg = A * d_len 

            # H_0 term (Renormalization)
            factor_0 = jv(0, z_arg)
            if self._nspin == 1:
                amp_0 = bare_amp * factor_0
            else:
                amp_0 = bare_amp * factor_0
            
            self.set_hop(amp_0, ind_i, ind_j, ind_R, mode="add", allow_conjugate_pair=True)

            # --- Prepare H_1 Operator (for 2nd Order) ---
            if order >= 2:
                # 1. Forward term (i -> j)
                # Phase factor: exp(-i * sigma * phi)
                factor_1_fwd = jv(1, z_arg) * np.exp(-1j * sigma * phi)
                val_fwd = bare_amp * factor_1_fwd
                H1_ops.append((val_fwd, ind_i, ind_j, np.array(ind_R)))

                # 2. Backward term (j -> i)
                # Geometry: d_ji = -d_ij, so phi_back = phi + pi
                # Phase factor: exp(-i * sigma * (phi + pi)) = - exp(-i * sigma * phi)
                factor_1_back = jv(1, z_arg) * np.exp(-1j * sigma * (phi + np.pi))
                
                # Bare amplitude: conjugate of forward
                if self._nspin == 1:
                    bare_amp_back = np.conj(bare_amp)
                else:
                    bare_amp_back = np.transpose(np.conj(bare_amp))
                
                val_back = bare_amp_back * factor_1_back
                H1_ops.append((val_back, ind_j, ind_i, -np.array(ind_R)))

        # Handle Onsite energies for Order 1 (static part)
        for i in range(self._norb):
            self._add_onsite_matrix(i, self._bare_site_energies[i])

        # --- Second Order Calculation ---
        if order >= 2:
            self._compute_second_order_commutator(H1_ops, omega)

    def _compute_second_order_commutator(self, H1_ops, omega):
        """
        Computes 1/(hbar*omega) * [H_1, H_-1] where H_-1 = H_1^dagger.
        """
        # H1_ops now explicitly contains ALL transitions (i->j and j->i)
        # We need to construct H_-1 (H minus 1) which is H_1^dagger
        
        Hm1_ops = []
        for amp, i, j, R in H1_ops:
            # H_-1 is Hermitian conjugate of H_1
            # Element <j|H_-1|i>(-R) = (<i|H_1|j>(R))*
            if self._nspin == 1:
                amp_dag = np.conj(amp)
            else:
                amp_dag = np.transpose(np.conj(amp))
            # Ensure R is numpy array for negation
            R_arr = np.array(R) if not isinstance(R, np.ndarray) else R
            Hm1_ops.append((amp_dag, j, i, -R_arr))
            
        # Compute A = H1 * Hm1
        Prod1 = self._multiply_operators(H1_ops, Hm1_ops)
        
        # Compute B = Hm1 * H1
        Prod2 = self._multiply_operators(Hm1_ops, H1_ops)
        
        # Commutator = (Prod1 - Prod2) / omega
        scale = 1.0 / omega
        
        all_keys = set(Prod1.keys()).union(set(Prod2.keys()))
        
        for key in all_keys:
            val1 = Prod1.get(key, 0.0)
            val2 = Prod2.get(key, 0.0)
            diff = (val1 - val2) * scale
            
            # Filter small numerical noise
            if np.linalg.norm(diff) < 1e-10:
                continue
                
            i, j, R_tuple = key
            
            # Canonical check to verify we don't double count 
            # (PythTB set_hop adds the conjugate pair automatically)
            if not self._is_canonical(i, j, R_tuple):
                continue
            
            # Onsite terms
            if i == j and all(r == 0 for r in R_tuple):
                self._add_onsite_matrix(i, diff)
            else:
                self.set_hop(diff, i, j, np.array(R_tuple), mode="add", allow_conjugate_pair=True)

    def _multiply_operators(self, op_list_A, op_list_B):
        """
        Multiplies two operator lists A and B.
        Returns a dictionary {(i, j, R_tuple): amplitude} representing A*B.
        Note: op_list structure is (amp, i, j, R) where R is np.array
        """
        res = {}
        
        # Optimize lookup for B
        # Map: start_node -> list of (amp, end_node, R)
        adj_B = {n: [] for n in range(self._norb)}
        for amp, start, end, R in op_list_B:
            adj_B[start].append((amp, end, R))
            
        # Iterate A
        for amp_A, i, k, R_A in op_list_A:
            # Look for k -> j in B
            if k in adj_B:
                for amp_B, j, R_B in adj_B[k]:
                    # Ensure R_A and R_B are numpy arrays
                    R_A_arr = np.array(R_A) if not isinstance(R_A, np.ndarray) else R_A
                    R_B_arr = np.array(R_B) if not isinstance(R_B, np.ndarray) else R_B
                    R_total = tuple((R_A_arr + R_B_arr).astype(int))
                    
                    if self._nspin == 1:
                        product = amp_A * amp_B
                    else:
                        product = np.dot(amp_A, amp_B) # Matrix multiplication
                        
                    self._add_to_dict(res, (i, j, R_total), product)
        return res

    def _add_to_dict(self, d, key, val):
        if key in d:
            d[key] += val
        else:
            d[key] = val

    def _add_onsite_matrix(self, ind, val):
        """Helper to add scalar or matrix to site energy."""
        if self._nspin == 1:
            # val might be complex from commutator, but effective H should be Hermitian.
            # Onsite terms must be real (or Hermitian matrices).
            # [H1, H-1] is Hermitian, so diagonal elements are real.
            self._site_energies[ind] += np.real(val)
        else:
            # Ensure it's treated as matrix
            self._site_energies[ind] += val

    def _is_canonical(self, i, j, R_tuple):
        """
        Determines if a hopping is the 'primary' one to pass to set_hop
        to avoid double counting with allow_conjugate_pair=True.
        PythTB usually takes i, j, R. It implies j, i, -R.
        We define canonical as: i < j, or (i==j and first non-zero R > 0).
        """
        if i < j:
            return True
        elif i > j:
            return False
        else:
            # i == j, check R
            # If R is all zeros, it's onsite, handled separately usually, but here True
            if all(r == 0 for r in R_tuple):
                return True
            # Find first non-zero
            for r in R_tuple:
                if r > 0: return True
                if r < 0: return False
            return True # Should not reach here if not all zeros

    def plotbands(self, kpath, label="Floquet Band Structure", n_points=300, A=None, omega=None, proj_spin=False):
        r"""
        Plot the band structure along a given k-path.
        
        :param kpath: List of k-points defining the path, e.g., [[0,0], [0.5,0.5], [0,0]]
        :param label: Title label for the plot (default: "Floquet Band Structure")
        :param n_points: Number of k-points along the path (default: 300)
        :param A: Optional driving amplitude for title display
        :param omega: Optional driving frequency for title display
        :param proj_spin: If True, project bands onto spin sz and color-code by spin value (default: False)
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        
        # Generate k-path
        (k_vec, k_dist, k_node) = self.k_path(kpath, n_points, report=False)
        
        # Check if spin projection is requested
        if proj_spin:
            if self._nspin != 2:
                raise ValueError("proj_spin=True requires nspin=2 (spinful calculation)")
            
            # Solve for eigenvalues and eigenvectors
            evals, evecs = self.solve_all(k_vec, eig_vectors=True)
            
            # Construct sz operator
            # Basis order: 1up, 1dn, 2up, 2dn, ...
            # sz = diag([1, -1, 1, -1, ...])
            n_bands = evals.shape[0]
            n_kpts = evals.shape[1]
            sz_operator = np.zeros((self._norb * 2, self._norb * 2), dtype=float)
            for i in range(self._norb):
                sz_operator[2*i, 2*i] = 1.0    # up
                sz_operator[2*i+1, 2*i+1] = -1.0  # down
            
            # Calculate spin expectation values for each band and k-point
            sz_expectation = np.zeros((n_bands, n_kpts))
            for k_idx in range(n_kpts):
                for band_idx in range(n_bands):
                    # evecs shape: [band, kpoint, orbital, spin]
                    # Reshape to [orbital*spin] for this band and kpoint
                    psi = evecs[band_idx, k_idx, :, :].flatten()
                    # Calculate <psi|sz|psi>
                    sz_expectation[band_idx, k_idx] = np.real(np.dot(psi.conj(), np.dot(sz_operator, psi)))
            
            # Create Red-White-Blue colormap
            colors_rwb = ['#FF0000', '#FFFFFF', '#0000FF']  # Red, White, Blue
            n_bins = 256
            cmap_rwb = LinearSegmentedColormap.from_list('RedWhiteBlue', colors_rwb, N=n_bins)
            
            # Plotting with scatter
            fig, ax = plt.subplots()
            for band_idx in range(n_bands):
                scatter = ax.scatter(k_dist, evals[band_idx], 
                                    c=sz_expectation[band_idx, :], 
                                    cmap=cmap_rwb, 
                                    vmin=-1, vmax=1,
                                    s=2, edgecolors='none', alpha=0.8)
            
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('$\\langle S_z \\rangle$', rotation=270, labelpad=20)
            
        else:
            # Solve for eigenvalues only
            evals = self.solve_all(k_vec)
            
            print("Effective Hoppings (First few):")
            # Just printing some internal data to verify
            for i, h in enumerate(self._hoppings[:5]):
                print(f"Hop {i}: sites {h[1]}->{h[2]}, R={h[3]}, Amp={np.round(h[0], 4)}")

            # Plotting
            fig, ax = plt.subplots()
            for band_idx in range(len(evals)):
                ax.plot(k_dist, evals[band_idx], "b-", label=f'Band {band_idx + 1}')
        
        # Build title
        title = label
        if A is not None and omega is not None:
            title += f"\nA={A}, $\\omega$={omega}"
        elif A is not None:
            title += f"\nA={A}"
        elif omega is not None:
            title += f"\n$\\omega$={omega}"
        
        ax.set_title(title)
        ax.set_ylabel("Energy (eV)")
        ax.set_xlabel("k-path")
        
        # Draw vertical lines for high symmetry points
        for node in k_node:
            ax.axvline(node, color='k', linestyle='--', linewidth=0.5)
        
        if not proj_spin:
            plt.legend()
        # plt.show()
        return fig, ax

    # ======================================================================
    # Topology Calculation Methods
    # ======================================================================

    def calculate_wilson_loop(self, mesh_size=51, occ=None, dir=1, start_k=[0.0, 0.0], 
                              contin=True, return_plot=False, plot_kwargs=None):
        """
        Calculate Wilson loop (Wannier centers) for the Floquet model.
        
        Parameters:
        -----------
        mesh_size : int
            Size of k-space mesh (default: 51)
        occ : list of int or None
            List of occupied band indices. If None, uses all bands (default: None)
        dir : int
            Direction along which to calculate Wilson loop (default: 1, i.e., ky direction)
        start_k : list of float
            Origin of k-space grid (default: [0.0, 0.0])
        contin : bool
            Whether to make phases continuous (default: True)
        return_plot : bool
            Whether to return figure and axis objects (default: False)
        plot_kwargs : dict or None
            Additional keyword arguments for plotting (default: None)
        
        Returns:
        --------
        wilson_loop : ndarray
            Wilson loop eigenvalues, shape [mesh_size, n_bands]
        kx_abs_vals : ndarray
            Absolute kx coordinates for plotting
        wilson_loop_total : ndarray
            Total Wilson loop (sum over all bands), shape [mesh_size]
        fig, ax : matplotlib figure and axis (if return_plot=True)
        """
        from pythtb import wf_array
        import matplotlib.pyplot as plt
        
        # Create wf_array object
        wf = wf_array(self, [mesh_size, mesh_size])
        
        # Solve on regular grid
        wf.solve_on_grid(start_k)
        
        # Calculate reciprocal lattice vectors for coordinate conversion
        lat = self._lat
        lat_matrix = np.array(lat)
        lat_matrix_T = lat_matrix.T
        rec_lat_matrix = 2 * np.pi * np.linalg.inv(lat_matrix_T)
        
        # Calculate Wilson loop eigenvalues (individual bands)
        if occ is None:
            wilson_loop = wf.berry_phase(occ="All", dir=dir, berry_evals=True, contin=contin)
            wilson_loop_total = wf.berry_phase(occ="All", dir=dir, berry_evals=False, contin=contin)
        else:
            wilson_loop = wf.berry_phase(occ=occ, dir=dir, berry_evals=True, contin=contin)
            wilson_loop_total = wf.berry_phase(occ=occ, dir=dir, berry_evals=False, contin=contin)
        
        # Convert kx to absolute coordinates
        kx_reduced_vals = np.linspace(0, 1, mesh_size)
        kx_abs_vals = kx_reduced_vals * rec_lat_matrix[0, 0]
        
        if return_plot:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
            
            # Plot individual band Wilson loops in first subplot
            for band_idx in range(wilson_loop.shape[1]):
                # Wrap Wannier centers to [-0.5, 0.5] range
                wannier_center = wilson_loop[:, band_idx] / (2 * np.pi)
                wannier_center_wrapped = ((wannier_center + 0.5) % 1.0) - 0.5
                ax1.plot(kx_abs_vals, wannier_center_wrapped, 'o', 
                       label=f'Band {band_idx + 1}', markersize=3)
            
            ax1.set_xlabel('$k_x$ (absolute coordinates)')
            ax1.set_ylabel('Wannier Center (fraction of unit cell)')
            ax1.set_ylim(-0.5, 0.5)
            ax1.set_yticks([-0.5, -0.25, 0, 0.25, 0.5])
            ax1.set_yticklabels(['$-\\pi$', '$-\\pi/2$', '$0$', '$\\pi/2$', '$\\pi$'])
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
            ax1.axhline(y=0.5, color='k', linestyle='--', linewidth=0.5)
            ax1.set_title('Individual Bands')
            
            # Plot total Wilson loop (sum of all bands) in second subplot
            wannier_center_total = wilson_loop_total / (2 * np.pi)
            wannier_center_total_wrapped = ((wannier_center_total + 0.5) % 1.0) - 0.5
            ax2.plot(kx_abs_vals, wannier_center_total_wrapped, 'o', 
                   label='Total', color='red', alpha=1)
            
            ax2.set_xlabel('$k_x$ (absolute coordinates)')
            ax2.set_ylabel('Wannier Center (fraction of unit cell)')
            ax2.set_ylim(-0.5, 0.5)
            ax2.set_yticks([-0.5, -0.25, 0, 0.25, 0.5])
            ax2.set_yticklabels(['$-\\pi$', '$-\\pi/2$', '$0$', '$\\pi/2$', '$\\pi$'])
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
            ax2.axhline(y=0.5, color='k', linestyle='--', linewidth=0.5)
            ax2.set_title('Total (Sum of All Bands)')
            
            plt.tight_layout()
            
            return wilson_loop, kx_abs_vals, fig, (ax1, ax2), wilson_loop_total
        
        return wilson_loop, kx_abs_vals, wilson_loop_total

    def calculate_chern_number(self, mesh_size=51, occ=None, start_k=[0.0, 0.0], dirs=None):
        """
        Calculate Chern number for the Floquet model.
        
        Parameters:
        -----------
        mesh_size : int
            Size of k-space mesh (default: 51)
        occ : list of int or None
            List of occupied band indices. If None, uses all bands (default: None)
        start_k : list of float
            Origin of k-space grid (default: [0.0, 0.0])
        dirs : list of int or None
            Directions for Berry flux calculation. If None, uses [0, 1] (default: None)
        
        Returns:
        --------
        chern_number : float
            Chern number (Berry flux / (2*pi))
        berry_flux : float
            Total Berry flux
        """
        from pythtb import wf_array
        
        # Create wf_array object
        wf = wf_array(self, [mesh_size, mesh_size])
        
        # Solve on regular grid
        wf.solve_on_grid(start_k)
        
        # Calculate Berry flux
        if occ is None:
            berry_flux = wf.berry_flux(occ="All", dirs=dirs)
        else:
            berry_flux = wf.berry_flux(occ=occ, dirs=dirs)
        
        # Chern number = Berry flux / (2*pi)
        chern_number = berry_flux / (2 * np.pi)
        
        return chern_number, berry_flux

    def calculate_berry_curvature(self, mesh_size=51, occ=None, start_k=[0.0, 0.0], 
                                  dirs=None, return_plot=False, plot_kwargs=None, log=False):
        """
        Calculate Berry curvature distribution for the Floquet model.
        
        Parameters:
        -----------
        mesh_size : int
            Size of k-space mesh (default: 51)
        occ : list of int or None
            List of occupied band indices. If None, uses all bands (default: None)
        start_k : list of float
            Origin of k-space grid (default: [0.0, 0.0])
        dirs : list of int or None
            Directions for Berry flux calculation. If None, uses [0, 1] (default: None)
        return_plot : bool
            Whether to return figure and axis objects (default: False)
        plot_kwargs : dict or None
            Additional keyword arguments for plotting (default: None)
        log: bool
            Whether to use log scale for plotting (default: False)

        Returns:
        --------
        berry_curvature_density : ndarray
            Berry curvature density, shape [mesh_size-1, mesh_size-1]
        KX, KY : ndarray
            Absolute k-space coordinates for plotting
        fig, ax : matplotlib figure and axis (if return_plot=True)
        """
        from pythtb import wf_array
        import matplotlib.pyplot as plt
        
        # Create wf_array object
        wf = wf_array(self, [mesh_size, mesh_size])
        
        # Solve on regular grid
        wf.solve_on_grid(start_k)
        
        # Calculate reciprocal lattice vectors for coordinate conversion
        lat = self._lat
        lat_matrix = np.array(lat)
        lat_matrix_T = lat_matrix.T
        rec_lat_matrix = 2 * np.pi * np.linalg.inv(lat_matrix_T)
        
        # Get individual Berry phases for each plaquette
        if occ is None:
            berry_curvature = wf.berry_flux(occ="All", dirs=dirs, individual_phases=True)
        else:
            berry_curvature = wf.berry_flux(occ=occ, dirs=dirs, individual_phases=True)
        
        # Convert to Berry curvature (divide by plaquette area)
        dk = 1.0 / mesh_size  # step size in reduced coordinates
        plaquette_area_abs = abs(np.linalg.det(rec_lat_matrix)) * dk * dk
        berry_curvature_density = berry_curvature / plaquette_area_abs
        
        # Create k-space grid in reduced coordinates
        kx_reduced = np.linspace(0, 1, mesh_size - 1) + 0.5 * dk
        ky_reduced = np.linspace(0, 1, mesh_size - 1) + 0.5 * dk
        KX_reduced, KY_reduced = np.meshgrid(kx_reduced, ky_reduced, indexing='ij')
        
        # Convert to absolute coordinates
        KX_abs = (KX_reduced * rec_lat_matrix[0, 0] + KY_reduced * rec_lat_matrix[0, 1])
        KY_abs = (KX_reduced * rec_lat_matrix[1, 0] + KY_reduced * rec_lat_matrix[1, 1])
        
        KX, KY = KX_abs, KY_abs
        
        if log:
            # For log scale: positive values -> log(x), negative values -> -log(|x|)
            sign = np.sign(berry_curvature_density)
            abs_values = np.abs(berry_curvature_density)
            
            valid_mask = (abs_values > 0) & np.isfinite(abs_values)
            min_valid = np.min(abs_values[valid_mask]) if np.any(valid_mask) else 1e-10
            small_value = min(min_valid * 0.1, 1e-10)
            abs_values = np.where((abs_values == 0) | ~np.isfinite(abs_values), small_value, abs_values)
            
            log_abs_values = np.log(abs_values)
            berry_curvature_density = sign * log_abs_values
            
            berry_curvature_density = np.where(np.isfinite(berry_curvature_density), 
                                              berry_curvature_density, 0.0)
        
        if return_plot:
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Calculate symmetric color range
            finite_values = berry_curvature_density[np.isfinite(berry_curvature_density)]
            if len(finite_values) > 0:
                vmax = np.max(np.abs(finite_values))
                vmin = -vmax
            else:
                vmax = 1.0
                vmin = -1.0
            
            # Default plot kwargs
            default_kwargs = {
                'levels': 50,
                'cmap': 'RdBu_r',
                'vmin': vmin,
                'vmax': vmax
            }
            if plot_kwargs is not None:
                default_kwargs.update(plot_kwargs)
            
            im = ax.contourf(KX, KY, berry_curvature_density, **default_kwargs)
            ax.set_xlabel('$k_x$ (absolute coordinates)')
            ax.set_ylabel('$k_y$ (absolute coordinates)')
            
            # Set symmetric limits
            xyrange = np.max((np.abs(KX), np.abs(KY)))
            ax.set_xlim(-xyrange, xyrange)
            ax.set_ylim(-xyrange, xyrange)
            
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Berry Curvature')
            plt.tight_layout()
            
            return berry_curvature_density, KX, KY, fig, ax
        
        return berry_curvature_density, KX, KY

    def calculate_all_topology(self, mesh_size=51, occ=None, start_k=[0.0, 0.0], 
                              return_plots=False, plot_kwargs=None, log=False):
        """
        Calculate all topological properties: Wilson loop, Chern number, and Berry curvature.
        
        Parameters:
        -----------
        mesh_size : int
            Size of k-space mesh (default: 51)
        occ : list of int or None
            List of occupied band indices. If None, uses all bands (default: None)
        start_k : list of float
            Origin of k-space grid (default: [0.0, 0.0])
        return_plots : bool
            Whether to return figure and axis objects (default: False)
        plot_kwargs : dict or None
            Additional keyword arguments for plotting (default: None)
        log: bool
            Whether to use log scale for plotting (default: False)
            
        Returns:
        --------
        results : dict
            Dictionary containing:
            - 'wilson_loop': Wilson loop eigenvalues (individual bands)
            - 'wilson_loop_total': Total Wilson loop (sum of all bands)
            - 'kx_abs': Absolute kx coordinates for Wilson loop
            - 'chern_number': Chern number
            - 'berry_flux': Total Berry flux
            - 'berry_curvature': Berry curvature density
            - 'KX', 'KY': Absolute k-space coordinates for Berry curvature
            - 'fig_wilson', 'ax_wilson': Figure and tuple of axes (ax1, ax2) for Wilson loop (if return_plots=True)
            - 'fig_berry', 'ax_berry': Figure and axis for Berry curvature (if return_plots=True)
        """
        results = {}
        
        # Calculate Wilson loop
        if return_plots:
            wilson_loop, kx_abs, fig_wilson, ax_wilson, wilson_loop_total = self.calculate_wilson_loop(
                mesh_size, occ, start_k=start_k, return_plot=True, plot_kwargs=plot_kwargs
            )
            results['fig_wilson'] = fig_wilson
            results['ax_wilson'] = ax_wilson
        else:
            wilson_loop, kx_abs, wilson_loop_total = self.calculate_wilson_loop(
                mesh_size, occ, start_k=start_k, return_plot=False
            )
        results['wilson_loop'] = wilson_loop
        results['wilson_loop_total'] = wilson_loop_total
        results['kx_abs'] = kx_abs
        
        # Calculate Chern number
        chern_number, berry_flux = self.calculate_chern_number(mesh_size, occ, start_k)
        results['chern_number'] = chern_number
        results['berry_flux'] = berry_flux
        
        # Calculate Berry curvature
        if return_plots:
            berry_curvature, KX, KY, fig_berry, ax_berry = self.calculate_berry_curvature(
                mesh_size, occ, start_k=start_k, return_plot=True, plot_kwargs=plot_kwargs, log=log
            )
            results['fig_berry'] = fig_berry
            results['ax_berry'] = ax_berry
        else:
            berry_curvature, KX, KY = self.calculate_berry_curvature(
                mesh_size, occ, start_k=start_k, return_plot=False, log=log
            )
        results['berry_curvature'] = berry_curvature
        results['KX'] = KX
        results['KY'] = KY
        
        return results
