module sampling_lines
    implicit none
contains

    subroutine binary_search(x, arr, n, j, i_err)
         implicit none
         real(8), intent(in) :: x
         real(8), intent(in) :: arr(:)
         integer, intent(in) :: n
         integer :: low, high, mid
         integer, intent(out) :: j, i_err


         low = 1
         high = n - 1

         do while (low <= high)

             mid = (low + high) / 2

             if (x >= arr(mid) .and. x <= arr(mid+1)) then
                 j = mid
                 return
             end if

             if (x < arr(mid)) then

                 high = mid - 1

             else
                 low = mid + 1
             end if

         end do

         j = 1
         i_err = 4

    end subroutine binary_search



    subroutine intp_c_corr(N_lines, N_grid_sig, N_grid_gamosig, sigma_grid, gamosig_grid, C_corr_grid, gamma_rsig_lines, &
            sigma_lines, C_corr_lines)

        implicit none
        integer, intent(in) :: N_grid_sig, N_grid_gamosig, N_lines
        real(8), intent(in) :: sigma_grid(:), gamosig_grid(:)
        real(8), intent(in) :: C_corr_grid(:, :)
        real(8), intent(out) :: C_corr_lines(N_lines)
        real(8), intent(in) :: gamma_rsig_lines(:), sigma_lines(:)


        real(8) :: log_sig_min, log_sig_max, log_gamr_min, log_gamr_max, sig_param, gamma_rsig_param
        real(8) :: C11, C21, C12, C22
        integer :: sig_ind, gamosig_ind
        integer :: i

        log_sig_min = log10(sigma_grid(1))
        log_sig_max = log10(sigma_grid(N_grid_sig))
        log_gamr_min = log10(gamosig_grid(1))
        log_gamr_max = log10(gamosig_grid(N_grid_gamosig))

        ! Loop over the lines
        do i = 1, N_lines
            sig_ind = int(((log10(sigma_lines(i)) - log_sig_min) / (log_sig_max - log_sig_min) * dble(N_grid_sig - 1)) + 1)

            if (sigma_lines(i) <= sigma_grid(1)) then
                sig_ind = 1
                sig_param = 0.0d0
            else if (sigma_lines(i) >= sigma_grid(N_grid_sig)) then
                sig_ind = N_grid_sig - 1
                sig_param = 1.0d0
            else
                sig_param = (sigma_lines(i) - sigma_grid(sig_ind)) / &
                            (sigma_grid(sig_ind+1) - sigma_grid(sig_ind))
            end if


            gamosig_ind = int(((log10(gamma_rsig_lines(i)) - log_gamr_min) / &
                    (log_gamr_max - log_gamr_min) * dble(N_grid_gamosig - 1)) + 1)

            if (gamma_rsig_lines(i) <= gamosig_grid(1)) then
                gamosig_ind = 1
                gamma_rsig_param = 0.0d0
            else if (gamma_rsig_lines(i) >= gamosig_grid(N_grid_gamosig)) then
                gamosig_ind = N_grid_gamosig - 1
                gamma_rsig_param = 1.0d0
            else
                gamma_rsig_param = (gamma_rsig_lines(i) - gamosig_grid(gamosig_ind)) / &
                                   (gamosig_grid(gamosig_ind+1) - gamosig_grid(gamosig_ind))
            end if

            sig_ind = min(sig_ind, N_grid_sig - 1)
            sig_ind = max(sig_ind, 1)
            gamosig_ind = min(gamosig_ind, N_grid_gamosig - 1)
            gamosig_ind = max(gamosig_ind, 1)


            C11 = C_corr_grid(sig_ind, gamosig_ind)
            C21 = C_corr_grid(sig_ind + 1, gamosig_ind)
            C12 = C_corr_grid(sig_ind, gamosig_ind + 1)
            C22 = C_corr_grid(sig_ind + 1, gamosig_ind + 1)

            C_corr_lines(i) = (1 - sig_param)*(1 - gamma_rsig_param)*C11 + sig_param*(1 - gamma_rsig_param)*C21 + &
                    (1 - sig_param)*gamma_rsig_param*C12 + sig_param*gamma_rsig_param*C22

        end do

    end subroutine intp_c_corr


    subroutine sample_lines(N_lines_per_pack, N_grid_pack_log, N_grid_pack_lin, N_rd_numbers, res, sigma_G_pack, gamma_L_pack, &
                    w_number_eff_pack, S_pack, pack_w_number_log, bin_width_pack_log, bin_bound_pack_log, pack_w_number_lin, &
                    bin_bound_pack_lin, pack_tot_log, pack_tot_lin, cutoff, del_therm_rd, del_press_rd, line_density, &
                    lin_grid, sampling_boost)
        ! """
        ! Routine to samples the lines of one pack of lines
        ! It can calculate it on a logarithmic and a linear grid, depending on 'lin_grid'
        ! The technique used is proposed in Min (2017)
        ! """

        implicit none

        ! input parameters
        integer, intent(in) :: N_lines_per_pack, N_grid_pack_log, N_grid_pack_lin
        integer(8), intent(in) :: N_rd_numbers
        real(8), intent(in) :: res, cutoff, sampling_boost
        logical, intent(in) :: lin_grid

        real(8), intent(in) :: sigma_G_pack(:), gamma_L_pack(:), w_number_eff_pack(:), S_pack(:), line_density(:)
        real(8), intent(in) :: pack_w_number_log(:), bin_width_pack_log(:), pack_w_number_lin(:)
        real(8), intent(inout) :: pack_tot_log(:), pack_tot_lin(:)

        real(8), intent(in) :: del_therm_rd(:), del_press_rd(:)
        real(8), intent(in) :: bin_bound_pack_log(:), bin_bound_pack_lin(:)

        ! variables
        real(8) :: w_number_pack_1, log_w_number_pack_1_res, S_pack_av, gamma_L_av

        ! arrays for grid and line properties
        real(8), dimension(N_grid_pack_log) :: inverse_bin_width_pack_log

        ! sampling parameters
        real(8) :: del_therm, del_press, del_nu1, del_nu2, f_low, f_high, w
        real(8) :: rand_num, del_press_sq, index_del_nu1_float, index_del_nu2_float

        ! additional variables
        real(8) :: sigma_G_i, gamma_L_i, gamma_L_i_sq, w_number_eff_i, norm_factor_log, norm_factor_lin
        real(8) :: S_ratio, log_N_grid_pack

        real(8) :: left_limit_log, right_limit_log, diff_delnus, diff_floats, taylor, del_lin
        real(8) :: left_limit_lin, right_limit_lin
        integer :: left_limit_log_id, right_limit_log_id, left_limit_lin_id, right_limit_lin_id

        ! integers needed for loops and indexing
        integer :: i, index_del_nu1, index_del_nu2, max_index, min_index
        integer(8) :: N_samples, rand_index, j

        ! Define parameters to increase speed
        w_number_pack_1 = pack_w_number_log(1)
        log_w_number_pack_1_res = log(w_number_pack_1) * res
        inverse_bin_width_pack_log = 1.0d0 / bin_width_pack_log
        log_N_grid_pack = log(real(N_grid_pack_log))

        ! Average of intensities and gamma broadening to determine number of samples
        S_pack_av = sum(S_pack) / N_lines_per_pack
        gamma_L_av = sum(gamma_L_pack) / N_lines_per_pack

        ! Resolution of the linear grid
        del_lin = pack_w_number_lin(2) - pack_w_number_lin(1)

        ! Loop over the lines in the pack, claculating the line profiles
        do i = 1, N_lines_per_pack

                ! Define parameters to increase speed
                sigma_G_i = sigma_G_pack(i)
                gamma_L_i = gamma_L_pack(i)
                gamma_L_i_sq = gamma_L_pack(i) ** 2
                w_number_eff_i = w_number_eff_pack(i)

                ! Ratio of the intensity to the average intensity
                S_ratio = S_pack(i) / S_pack_av

                ! Calculate the number of samples needed for the line profile and limit it between 0 and 1e7
                N_samples = int(1e-2 * S_ratio * res / (line_density(i) * (gamma_L_av + 0.005)**(1.5)), kind=8)
                N_samples = int(N_samples * (1 + 6 * (2000/w_number_eff_i)**1.6) * sampling_boost, kind=8)
                N_samples = min(N_samples, 10000000)
                N_samples = max(N_samples, 1)

                ! Normalization factors for the line profile, so that the sampled line is directly normalized
                norm_factor_log = 2 * S_pack(i) * res / (w_number_eff_i * N_samples)
                norm_factor_lin = 2 * S_pack(i) / (del_lin * N_samples)

                ! Limits of the line profile due to cutoff
                left_limit_log = max(w_number_eff_i - cutoff, w_number_pack_1)
                right_limit_log = min(w_number_eff_i + cutoff, pack_w_number_log(N_grid_pack_log))

                left_limit_log_id = int(res * log(left_limit_log / w_number_pack_1) + 1.5)
                right_limit_log_id = int(res * log(right_limit_log / w_number_pack_1) + 1.5)


                ! Limit calculation for the linear grid
                left_limit_lin = max(w_number_eff_i - cutoff, pack_w_number_lin(1))
                right_limit_lin = min(w_number_eff_i + cutoff, pack_w_number_lin(N_grid_pack_lin))

                left_limit_lin_id = int((left_limit_lin - pack_w_number_lin(1)) / del_lin + 1.5)
                right_limit_lin_id = int((right_limit_lin - pack_w_number_lin(1)) / del_lin + 1.5)

                ! Use taylor expansion for very small gamma_L to avoid numerical cancelling
                taylor = 0.0

                if ((gamma_L_i/w_number_eff_i) <= 1.0d-7) then
                    taylor = 1.0
                end if

                ! Random number for a random index of the random numbers, continuing from this index then
                call random_number(rand_num)
                ! Important to subtract max number of samples to avoid indexing outside of the array
                rand_index = int(rand_num * (N_rd_numbers - 2.0d7), kind=8)

                ! Initialize the maximum and minimum index of the line profile
                max_index = 0
                min_index = N_grid_pack_log

                ! Calculation of the individual line for the logarithmic grid
                if (lin_grid .eqv. .FALSE.) then

                    do j = 1, N_samples

                        ! Calculate the random sample for the thermal and pressure broadening
                        del_therm = sigma_G_i * del_therm_rd(j + rand_index)
                        del_press = gamma_L_i * del_press_rd(j + rand_index)
                        del_press_sq = del_press ** 2

                        ! Calculate the left and right value of the sample and the difference
                        del_nu1 = w_number_eff_i + del_therm - abs(del_press)
                        del_nu2 = w_number_eff_i + del_therm + abs(del_press)
                        diff_delnus = 2 * abs(del_press)

                        ! Calculate the float index of the samples and their difference (if needed with taylor expansion)
                        index_del_nu1_float = res * log(del_nu1) - log_w_number_pack_1_res
                        index_del_nu2_float = res * log(del_nu2) - log_w_number_pack_1_res
                        diff_floats = taylor * (2 * res * abs(del_press) / (w_number_eff_i + del_therm)) + &
                                (1.0 - taylor) * (index_del_nu2_float - index_del_nu1_float)

                        ! Calculate the integer index of the samples
                        ! Check if the left index is greater than the right index (whole sample outside of the grid)
                        index_del_nu1 = int(index_del_nu1_float + 1.5)
                        if (index_del_nu1 >= right_limit_log_id) then
                            cycle
                        end if
                        ! Limit the left index to the left limit
                        index_del_nu1 = max(index_del_nu1, left_limit_log_id)

                        ! Check if the right index is smaller than the left index (whole sample outside of the grid)
                        index_del_nu2 = int(index_del_nu2_float + 1.5)
                        if (index_del_nu2 <= left_limit_log_id) then
                            cycle
                        end if
                        ! Limit the right index to the right limit
                        index_del_nu2 = min(index_del_nu2, right_limit_log_id)

                        ! Calculate the fraction of the sample that is in the left boundary bin
                        f_low = min((bin_bound_pack_log(index_del_nu1) - del_nu1) * &
                                inverse_bin_width_pack_log(index_del_nu1), 1.0d0)

                        ! Calculate the fraction of the sample that is in the right boundary bin
                        f_high = min((del_nu2 - bin_bound_pack_log(index_del_nu2-1)) * &
                                inverse_bin_width_pack_log(index_del_nu2), 1.0d0)

                        ! Calculate the weight of the samples
                        w = del_press_sq / (del_press_sq + gamma_L_i_sq) * norm_factor_log

                        ! Weight the weight by the spread over the bins
                        w = w / diff_floats

                        ! If the sample falls in one bin, add the weight to the bin
                        ! weighted by the fraction of the bin it actually covers
                        if (index_del_nu1 == index_del_nu2) then
                            pack_tot_log(index_del_nu1) = pack_tot_log(index_del_nu1) + w * (diff_delnus) * &
                                    inverse_bin_width_pack_log(index_del_nu1)

                            ! Stabitity check -> could be removed, if tested without. Does not impact the time
                            if (abs(pack_tot_log(index_del_nu1))>1.0d300) then
                                cycle
                            end if
                        ! If the sample falls in more than one bin, add the weight to all bins
                        ! The boundary bins are treated specially, as only the fraction that is actually covered is added
                        else
                            pack_tot_log(index_del_nu1+1:index_del_nu2-1) = pack_tot_log(index_del_nu1+1:index_del_nu2-1) + w
                            pack_tot_log(index_del_nu1) = pack_tot_log(index_del_nu1) + w * f_low
                            pack_tot_log(index_del_nu2) = pack_tot_log(index_del_nu2) + w * f_high

                        end if

                    end do

                end if


                ! Sampling of the individual line for the linear grid
                if (lin_grid .eqv. .TRUE.) then

                    do j = 1, N_samples


                        ! Calculate the random sample for the thermal and pressure broadening
                        del_therm = sigma_G_i * del_therm_rd(j + rand_index)
                        del_press = gamma_L_i * del_press_rd(j + rand_index)
                        del_press_sq = del_press ** 2

                        ! Calculate the left and right value of the sample and the difference
                        del_nu1 = w_number_eff_i + del_therm - abs(del_press)
                        del_nu2 = w_number_eff_i + del_therm + abs(del_press)
                        diff_delnus = 2 * abs(del_press)

                        ! Calculate the float index of the samples and their difference
                        index_del_nu1_float = (del_nu1 - pack_w_number_lin(1)) / del_lin
                        index_del_nu2_float = (del_nu2 - pack_w_number_lin(1)) / del_lin
                        diff_floats = 2 * abs(del_press) / del_lin

                        ! Calculate the integer index of the samples
                        ! Check if the left index is greater than the right index (whole sample outside of the grid)
                        index_del_nu1 = int(index_del_nu1_float + 1.5)
                        if (index_del_nu1 >= right_limit_lin_id) then
                            cycle
                        end if
                        ! Limit the left index to the left limit
                        index_del_nu1 = max(index_del_nu1, left_limit_lin_id)

                        ! todo potentially skip the if statement by cliping the indices to the limits and then skipping
                        ! todo the boundaries by extending the grid by one / replace them with the neighbouring bins.

                        ! Check if the right index is smaller than the left index (whole sample outside of the grid)
                        index_del_nu2 = int(index_del_nu2_float + 1.5)
                        if (index_del_nu2 <= left_limit_lin_id) then
                            cycle
                        end if
                        ! Limit the right index to the right limit
                        index_del_nu2 = min(index_del_nu2, right_limit_lin_id)

                        ! Calculate the fraction of the sample that is in the left boundary bin
                        f_low = min((bin_bound_pack_lin(index_del_nu1) - del_nu1) / del_lin, 1.0d0)

                        ! Calculate the fraction of the sample that is in the right boundary bin
                        f_high = min((del_nu2 - bin_bound_pack_lin(index_del_nu2-1)) / del_lin, 1.0d0)

                        ! Calculate the weight of the samples
                        w = del_press_sq / (del_press_sq + gamma_L_i_sq) * norm_factor_lin

                        ! Weight the weight by the spread of the bins
                        w = w / diff_floats

                        ! If the sample falls in one bin, add the weight to the bin
                        ! weighted by the fraction of the bin it actually covers
                        if (index_del_nu1 == index_del_nu2) then
                            pack_tot_lin(index_del_nu1) = pack_tot_lin(index_del_nu1) + w * (diff_delnus) / del_lin

                            ! Stabitity check -> could be removed, if tested without. Does not impact the time
                            if (abs(pack_tot_lin(index_del_nu1))>1.0d300) then
                                cycle
                            end if

                        ! If the sample falls in more than one bin, add the weight to all bins
                        ! The boundary bins are treated specially, as only the fraction that is actually covered is added
                        else
                            pack_tot_lin(index_del_nu1+1:index_del_nu2-1) = pack_tot_lin(index_del_nu1+1:index_del_nu2-1) + w
                            pack_tot_lin(index_del_nu1) = pack_tot_lin(index_del_nu1) + w * f_low
                            pack_tot_lin(index_del_nu2) = pack_tot_lin(index_del_nu2) + w * f_high

                        end if

                    end do


                end if


        end do

    end subroutine sample_lines


    subroutine calc_packs(N_lines_per_pack, N_grid_pack_log, N_rd_numbers, nu, opa, del_therm_rd, del_press_rd, &
                            sigma_G_pack, gamma_L_pack, w_number_eff_pack, S_pack, res, index_pack_left, index_pack_right, &
                            cutoff, Hartmann, line_density, max_gam_rd, max_sig_rd, sampling_boost, c_g_switch, i_err)

        ! """
        ! Routine to initialize the line packs
        ! Implemented switch to linear grid, if needed (samples could be lower than zero -> problem with log)
        ! If linear grid is used -> interpolation to the logarithmic grid afterwards
        ! Hartmann treatment (Hartmann et al. 1998) is implemented in this routine, but for the whole pack
        ! -> very important that the pack with is quite low, so that the assumption that the pack behaves as one large
        !    line is valid. Recommondation: use at leat 100 packs for 100/cm
        ! """


        implicit none

        ! input parameters
        integer(8), intent(in) :: N_rd_numbers
        integer, intent(in) :: N_lines_per_pack, N_grid_pack_log
        integer, intent(in) :: index_pack_left, index_pack_right

        logical, intent(in) :: Hartmann, c_g_switch

        real(8), intent(in) :: nu(:)
        real(8), intent(inout) :: opa(:)
        integer, intent(out) :: i_err

        real(8), intent(in) :: del_therm_rd(:), del_press_rd(:)
        real(8), intent(in) :: sigma_G_pack(:), gamma_L_pack(:), w_number_eff_pack(:), S_pack(:)
        real(8), intent(in) :: line_density(:)
        real(8), intent(in) :: res, cutoff, max_gam_rd, max_sig_rd, sampling_boost

        ! integer for packing the lines
        real(8), dimension(N_grid_pack_log) :: pack_w_number_log, bin_width_pack_log, pack_tot_log, hartmann_grid_log
        real(8), dimension(N_grid_pack_log-1) :: bin_bound_pack_log
        real(8), allocatable :: pack_w_number_lin(:), bin_bound_pack_lin(:), pack_tot_lin(:)
        real(8) :: del_nu_lin, pack_w_number_log_1, expo, max_gam, max_sig, max_dist
        integer :: N_grid_pack_lin
        integer :: i, j, k

        logical :: lin_grid

        real(8) :: mean_voigt_width, mean_lorentz_width, mean_gauss_width, max_pack_grid_diff
        real(8) :: dnu_coarse, len_pack

        ! Hartmann variabels
        real(8) :: mid_grid, w_number_pack_1, N_corr, O_area
        integer :: hartmann_id_60left, hartmann_id_26left, hartmann_id_26right, hartmann_id_60right

        ! Maximum values for the gaussian and lorentzian broadening
        max_gam = maxval(abs(gamma_L_pack))
        max_sig = maxval(abs(sigma_G_pack))

        ! Calculation of the maximum distance, to change to the log grid if needed.
        max_dist = max_gam * max_gam_rd + max_sig * max_sig_rd
        lin_grid = .FALSE.

        ! Initialize the grid of the pack
        pack_w_number_log = nu(index_pack_left:index_pack_right)
        pack_w_number_log_1 = nu(index_pack_left)

        pack_tot_log(:) = 0.0d0
        hartmann_grid_log = 1.0d0

        ! Check, if the maximum distance is smaller than the first effective wavenumber -> switch to linear grid
        if (w_number_eff_pack(1) <= max_dist) then
            lin_grid = .TRUE.

            del_nu_lin = nu(index_pack_left+1) - nu(index_pack_left)

            ! Number of grid points for the linear grid
            N_grid_pack_lin = int((pack_w_number_log(N_grid_pack_log) - pack_w_number_log(1)) / del_nu_lin) + 3

            if (N_grid_pack_lin < 0) then
                i_err = 2
                return
            end if

            ! Alloction of the linear grid arrays since the size is now known
            allocate(pack_w_number_lin(N_grid_pack_lin), bin_bound_pack_lin(N_grid_pack_lin-1), pack_tot_lin(N_grid_pack_lin))

            ! Initialize the linear grid
            pack_tot_lin = 0.0d0
            do i = 1, N_grid_pack_lin
                pack_w_number_lin(i) = pack_w_number_log_1 + del_nu_lin * (i - 2)
            end do

            bin_bound_pack_lin = (pack_w_number_lin(1:N_grid_pack_lin-1) + pack_w_number_lin(2:N_grid_pack_lin)) / 2.0d0

        else
            ! initializing a linear grid anyways, since it is required by the code
            ! # todo: bad programming, could be solved different?

            del_nu_lin = (nu(index_pack_right+1) - nu(index_pack_left)) / 11

            ! Number of grid points for the linear grid
            N_grid_pack_lin = 11

            ! Alloction of the linear grid arrays since the size is now known
            allocate(pack_w_number_lin(N_grid_pack_lin), bin_bound_pack_lin(N_grid_pack_lin-1), pack_tot_lin(N_grid_pack_lin))

            ! Initialize the linear grid
            pack_tot_lin = 0.0d0
            do i = 1, N_grid_pack_lin
                pack_w_number_lin(i) = pack_w_number_log_1 + del_nu_lin * (i - 2)
            end do

            bin_bound_pack_lin = (pack_w_number_lin(1:N_grid_pack_lin-1) + pack_w_number_lin(2:N_grid_pack_lin)) / 2.0d0

        end if

        ! Checking whats the average width of the lines -> if they are much broader than the grid use a coarser grid
        mean_lorentz_width = sum(gamma_L_pack) / N_lines_per_pack
        mean_gauss_width = sum(sigma_G_pack) / N_lines_per_pack
        mean_voigt_width = 0.5346 * mean_lorentz_width + sqrt(0.2166 * mean_lorentz_width**2 + mean_gauss_width**2)

        max_pack_grid_diff = pack_w_number_log(N_grid_pack_log) - pack_w_number_log(N_grid_pack_log-1)

        if ((mean_voigt_width/10 > max_pack_grid_diff) .and. c_g_switch) then
            ! Average line profile is much broader than grid -> coarser grid

            lin_grid = .TRUE.

            if (allocated(pack_w_number_lin)) then
                deallocate(pack_w_number_lin, bin_bound_pack_lin, pack_tot_lin)
            end if

            dnu_coarse = mean_voigt_width / 10
            len_pack = pack_w_number_log(N_grid_pack_log) - pack_w_number_log(1)

            ! + 3 for securing one wavenumber point outside of the log grid
            N_grid_pack_lin = int(len_pack / dnu_coarse) + 3

            if (N_grid_pack_lin < 0) then
                i_err = 3
                return
            end if

            !allocate(pack_w_number_lin(N_coarse_grid), bin_bound_pack_lin(N_coarse_grid-1), pack_tot_lin(N_coarse_grid))
            allocate(pack_w_number_lin(N_grid_pack_lin), bin_bound_pack_lin(N_grid_pack_lin-1), pack_tot_lin(N_grid_pack_lin))

            pack_tot_lin = 0.0d0
            do i = 1, N_grid_pack_lin
                pack_w_number_lin(i) = pack_w_number_log_1 + dnu_coarse * (i - 2)
            end do

            bin_bound_pack_lin = (pack_w_number_lin(1:N_grid_pack_lin-1) + pack_w_number_lin(2:N_grid_pack_lin)) / 2.0d0

        end if

        ! Calculate the bin width and the bin boundaries for the sampling process later
        bin_bound_pack_log = (pack_w_number_log(1:N_grid_pack_log-1) + pack_w_number_log(2:N_grid_pack_log)) / 2.0d0

        bin_width_pack_log(2:N_grid_pack_log-1) = bin_bound_pack_log(2:N_grid_pack_log-1) - bin_bound_pack_log(1:N_grid_pack_log-2)
        bin_width_pack_log(1) = (bin_bound_pack_log(1) - pack_w_number_log(1)) * 2.0d0
        bin_width_pack_log(N_grid_pack_log) = (pack_w_number_log(N_grid_pack_log) - bin_bound_pack_log(N_grid_pack_log-1)) * 2

        ! Calculate the line profiles of the lines in the pack
        call sample_lines(N_lines_per_pack, N_grid_pack_log, N_grid_pack_lin, N_rd_numbers, res, sigma_G_pack, gamma_L_pack, &
                    w_number_eff_pack, S_pack, pack_w_number_log, bin_width_pack_log, bin_bound_pack_log, pack_w_number_lin, &
                    bin_bound_pack_lin, pack_tot_log, pack_tot_lin, cutoff, del_therm_rd, del_press_rd, line_density, &
                    lin_grid, sampling_boost)

        ! If a linear grid is used, interpolate the line profiles to the logarithmic grid
        if (lin_grid .eqv. .TRUE.) then

            ! Changed the interpolation to the faster binary search method. Old interpolation is below, could be removed
            if (.FALSE.) then
                do i = 1, N_grid_pack_log

                    do j = 1, N_grid_pack_lin - 1


                        if ((pack_w_number_log(i) >= pack_w_number_lin(j)) .and. &
                                (pack_w_number_log(i) <= pack_w_number_lin(j+1))) then

                            if ((pack_tot_lin(j+1) == 0.0d0) .or. (pack_tot_lin(j) == 0.0d0)) then
                                pack_tot_log(i) = 0.0d0

                            else

                                expo = log(pack_w_number_log(i) / pack_w_number_lin(j)) * log(pack_tot_lin(j + 1) &
                                        / pack_tot_lin(j)) / log(pack_w_number_lin(j+1) / pack_w_number_lin(j))
                                pack_tot_log(i) = pack_tot_lin(j) * exp(expo)

                            end if

                            exit

                        end if

                    end do

                end do
            end if

            do i = 1, N_grid_pack_log

                call binary_search(pack_w_number_log(i), pack_w_number_lin, N_grid_pack_lin, j, i_err)

                    if (pack_tot_lin(j+1) == 0.0d0 .or. pack_tot_lin(j) == 0.0d0) then
                        pack_tot_log(i) = 0.0d0

                    else
                        expo = log(pack_w_number_log(i) / pack_w_number_lin(j)) * log(pack_tot_lin(j + 1) &
                                   / pack_tot_lin(j)) / log(pack_w_number_lin(j+1) / pack_w_number_lin(j))
                        pack_tot_log(i) = pack_tot_lin(j) * exp(expo)

                    end if

            end do

        end if

        ! Do the Hartmann treatment, but for the WHOLE pack!
        if (Hartmann .eqv. .TRUE.) then
            mid_grid = (pack_w_number_log(N_grid_pack_log) + pack_w_number_log(1)) / 2.0d0
            w_number_pack_1 = pack_w_number_log(1)

            ! calculate the boundaries of the hartmann correction grid
            ! Ensure that the arguments of the log aren't negative and only apply if the grid extends that far
            hartmann_id_60left = 1
            if ((mid_grid - 60) > 0) then

                hartmann_id_60left = int(res * log((mid_grid - 60) / w_number_pack_1) + 1.5)
                hartmann_id_60left = max(1, min(hartmann_id_60left, N_grid_pack_log))

                if (hartmann_id_60left > 1) then
                    hartmann_grid_log(1:hartmann_id_60left-1) = hartmann_grid_log(1:hartmann_id_60left-1) &
                        * 0.0684 * exp(-abs(pack_w_number_log(1:hartmann_id_60left-1) - mid_grid) / 393)

                end if

            end if

            if ((mid_grid - 26) > 0) then

                hartmann_id_26left = int(res * log((mid_grid - 26) / w_number_pack_1) + 1.5)
                hartmann_id_26left = max(1, min(hartmann_id_26left, N_grid_pack_log))

                hartmann_grid_log(hartmann_id_60left:hartmann_id_26left) = &
                    hartmann_grid_log(hartmann_id_60left:hartmann_id_26left) * 8.72 &
                    * exp(-abs(pack_w_number_log(hartmann_id_60left:hartmann_id_26left) - mid_grid) / 12)

            end if

            hartmann_id_60right = int(res * log((mid_grid + 60) / w_number_pack_1) + 1.5)
            hartmann_id_60right = max(1, min(hartmann_id_60right, N_grid_pack_log))

            if (hartmann_id_60right < N_grid_pack_log) then
                hartmann_grid_log(hartmann_id_60right:N_grid_pack_log) = hartmann_grid_log(hartmann_id_60right:N_grid_pack_log) &
                    * 0.0684 * exp(-abs(pack_w_number_log(hartmann_id_60right:N_grid_pack_log) - mid_grid) / 393)
            end if

            hartmann_id_26right = int(res * log((mid_grid + 26) / w_number_pack_1) + 1.5)
            hartmann_id_26right = max(1, min(hartmann_id_26right, N_grid_pack_log))

            if (hartmann_id_26right < N_grid_pack_log) then
                hartmann_grid_log(hartmann_id_26right:hartmann_id_60right-1) = &
                    hartmann_grid_log(hartmann_id_26right:hartmann_id_60right-1) * 8.72 &
                    * exp(-abs(pack_w_number_log(hartmann_id_26right:hartmann_id_60right-1) - mid_grid) / 12)
            end if

            ! Apply the Hartmann treatment to the pack profile
            N_corr = 0.0d0
            O_area = 0.0d0
            do k = 1, N_grid_pack_log
                N_corr = N_corr + pack_tot_log(k) * (1.0d0 - hartmann_grid_log(k)) * bin_width_pack_log(k)
                O_area = O_area + pack_tot_log(k) * bin_width_pack_log(k)
            end do

            N_corr = O_area / (O_area - N_corr)

            do k = 1, N_grid_pack_log
                pack_tot_log(k) = pack_tot_log(k) * hartmann_grid_log(k) * N_corr
            end do

        end if

        ! Add the line profile of the pack to the total opacity
        opa(index_pack_left:index_pack_right) = opa(index_pack_left:index_pack_right) + pack_tot_log

    end subroutine calc_packs




    subroutine calc_all_linepacks(N_lines, N_rd_numbers, N_grid, N_packs, N_lines_per_pack, N_lines_last_pack, res, nu, &
                                    S, gamma, sigma, del_therm_rd, del_press_rd, max_gam_rd, max_sig_rd, &
                                    effective_wavenumbers, line_density, cutoff, sampling_boost, hartmann, &
                                    c_g_switch, verbose, opa, i_err)
        ! """
        ! Routine to calculate the line opacity for a given grid
        ! The lines are packed in N_packs, each with N_lines_per_pack lines
        ! The last pack has N_lines_last_pack lines
        ! It requires that the lines are sorted in increasing order of wavenumber
        ! First, the gaussian and lorentzian broadening parameters are calculated
        ! The line profiles are calculated in the subroutine calc_packs
        ! The line profiles are sampled in the subroutine sample_lines
        ! """

        implicit none

        ! input parameters
        integer, intent(in) :: N_lines, N_grid, N_packs, N_lines_per_pack, N_lines_last_pack
        integer(8), intent(in) :: N_rd_numbers
        real(8), intent(in) :: res, cutoff, max_gam_rd, max_sig_rd, sampling_boost
        real(8), intent(in) :: nu(:), S(:), del_therm_rd(:), del_press_rd(:), line_density(:)
        real(8), intent(in) :: effective_wavenumbers(:), gamma(:), sigma(:)

        logical, intent(in) :: hartmann, c_g_switch, verbose

        ! output parameters
        integer, intent(out) :: i_err
        real(8), intent(out) :: opa(N_grid)

        real(8) :: nu_1, nu_N_grid

        ! integers needed for loops and indexing
        integer :: l

        ! integer for packing the lines
        integer :: index_pack_left, index_pack_right, N_grid_pack, Id_last_pack
        real(8) :: w_number_left, w_number_right
        real(8), dimension(N_lines_per_pack) :: sigma_G_pack, gamma_L_pack, w_number_eff_pack, S_pack, line_density_pack
        real(8), dimension(N_lines_last_pack) :: sigma_G_rpack, gamma_L_rpack, w_number_eff_rpack, S_rpack, &
                line_density_rpack

        Id_last_pack = N_lines_per_pack * N_packs

        ! Parameters to increase readability
        nu_1 = nu(1)
        nu_N_grid = nu(N_grid)
        opa = 0.0d0

        ! Loop over the packs of lines
        do l = 1, N_packs

            ! only proceed if there are lines in the pack
            if (N_lines_per_pack <= 0) then
                cycle
            end if

            if (verbose) then
                write(6,'(A,I0,A,I0, A, I0, A)', advance='no') &
                        'Progress: ', l, '/', N_packs, ' line packs (each containing ', N_lines_per_pack ,' lines)'
                write(6,'(A)', advance='no') char(13)
                call flush(6)
            end if

            ! Split the line list into packs
            w_number_eff_pack = effective_wavenumbers((N_lines_per_pack * (l - 1) + 1):N_lines_per_pack * l)
            sigma_G_pack = sigma((N_lines_per_pack * (l - 1) + 1):N_lines_per_pack * l)
            gamma_L_pack = gamma((N_lines_per_pack * (l - 1) + 1):N_lines_per_pack * l)
            S_pack = S((N_lines_per_pack * (l - 1) + 1):N_lines_per_pack * l)

            line_density_pack = line_density((N_lines_per_pack * (l - 1) + 1):N_lines_per_pack * l)

            ! Calculate the boundary wavenumbers of the pack and limit the indices to the grid boundaries
            w_number_left = max(w_number_eff_pack(1) - cutoff, nu_1)
            w_number_right = min(w_number_eff_pack(N_lines_per_pack) + cutoff, nu_N_grid)

            ! find the indices of the pack boundaries in the grid
            ! add 0.5 to ensure that the cutoff is fully included (not 1.5 to include the next point)
            index_pack_left = int(res * log(w_number_left/nu_1) + 0.5)
            index_pack_left = max(index_pack_left, 1)

            ! add 2.5 to ensure that the cutoff is fully included
            index_pack_right = int(res * log(w_number_right/nu_1) + 2.5)
            index_pack_right = min(index_pack_right, N_grid)

            N_grid_pack = index_pack_right - index_pack_left + 1

            ! Calculate the line profile of the pack
            call calc_packs(N_lines_per_pack, N_grid_pack, N_rd_numbers, nu, opa, del_therm_rd, del_press_rd, &
                            sigma_G_pack, gamma_L_pack, w_number_eff_pack, S_pack, res, index_pack_left, index_pack_right, &
                            cutoff, hartmann, line_density_pack, max_gam_rd, max_sig_rd, sampling_boost, c_g_switch, i_err)

        end do

        ! calculate the lines that are left -> last pack
        if (N_lines_last_pack > 0) then
            if (verbose) then
                write(6,*)
                write(*,*) 'Calculating last pack (containing, ', N_lines_last_pack, ' lines)!'
            end if

            w_number_eff_rpack = effective_wavenumbers(Id_last_pack+1:N_lines)

            sigma_G_rpack = sigma(Id_last_pack+1:N_lines)
            gamma_L_rpack = gamma(Id_last_pack+1:N_lines)
            S_rpack = S(Id_last_pack+1:N_lines)

            line_density_rpack = line_density(Id_last_pack+1:N_lines)

            w_number_left = max(w_number_eff_rpack(1) - cutoff, nu_1)
            w_number_right = min(w_number_eff_rpack(N_lines_last_pack) + cutoff, nu_N_grid)

            ! If the wavenumber range of the pack is too large then the hartmann treatment fails
            ! and the calculations take longer. Therefore an error is raised here.

            if ((w_number_eff_rpack(N_lines_last_pack) - w_number_eff_rpack(1)) > 5) then
                i_err = 1
                return
            end if

            ! Find indices of the pack with the remaining lines. Convention same as for the normal packs
            index_pack_left = int(res * log(w_number_left/nu_1) + 0.5)
            index_pack_left = max(index_pack_left, 1)

            index_pack_right = int(res * log(w_number_right/nu_1) + 2.5)
            index_pack_right = min(index_pack_right, N_grid)

            N_grid_pack = index_pack_right - index_pack_left + 1

            ! Calculate the line profile of the last pack
            call calc_packs(N_lines_last_pack, N_grid_pack, N_rd_numbers, nu, opa, del_therm_rd, del_press_rd, &
                                sigma_G_rpack, gamma_L_rpack, w_number_eff_rpack, S_rpack, res, index_pack_left, &
                                index_pack_right, cutoff, hartmann, line_density_rpack, max_gam_rd, max_sig_rd, &
                                sampling_boost, c_g_switch, i_err)

        end if

    end subroutine calc_all_linepacks


end module sampling_lines