module line_calculation_molliere2015
    implicit none
    contains
    subroutine phi_prime(gamma, sigma_D, w_number,lambda, n_lambda, phi_p, cutoff_str,cutoff)

      implicit none

      integer, intent(in) :: n_lambda
      double precision, intent(in) :: gamma, sigma_D, w_number
      double precision, intent(in) :: lambda(:)
      double precision, intent(out) :: phi_p(:)
      character(len=*), intent(in) :: cutoff_str
      double precision, intent(in) :: cutoff

      integer :: i
      double precision :: gamma_doppler, lambda_eff, b_sharp, pi
      COMPLEX(8) :: PRBFCT(n_lambda)

      ! p_shift_w_number = w_number+del_ref*p_atm
      pi = 3.14159265359d0


      lambda_eff = 1d0 / (w_number)
      b_sharp = 1d0
      ! gamma doppler from Kees' lecture. For this it holds that gamma_doppler = sqrt(2)sigma_doppler
      ! compared to the usual standard variation in the normal distribution

      gamma_doppler = sigma_D * sqrt(2d0)


      call HUMLICEK(n_lambda-1,(1d0/lambda - (1d0/lambda_eff))/gamma_doppler, &
                             gamma/gamma_doppler,PRBFCT)

      do i = 1, n_lambda

         phi_p(i) = b_sharp*REAL(PRBFCT(i))/sqrt(pi)/gamma_doppler

         ! Apply cutoff
         if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= cutoff) then
              phi_p(i) = 0d0
         end if

      end do

      if (cutoff_str == 'F') then
        ! hard cutoff
        !write(*,*) 'HARD CUTOFF (F) at ', cutoff
        do i = 1, n_lambda

           if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= cutoff) then
              phi_p(i) = 0d0
           end if

        end do

      else if (cutoff_str == 'H') then
        !write(*,*) 'HARTMANN CUTOFF'

        ! CUTOFF IMPLEMENTATION, following hartmann et al 2002: use this for ecerything except CO2
        do i = 1, n_lambda

           if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= 60d0) then
              phi_p(i) = phi_p(i)*0.0684d0*exp(-abs(1d0/lambda(i) - (1d0/lambda_eff))/393d0)
           else if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= 26d0) then
              phi_p(i) = phi_p(i)*8.72d0*exp(-abs(1d0/lambda(i) - (1d0/lambda_eff))/12d0)
           end if

        end do


      else if (cutoff_str == 'B') then
        !write(*,*) 'BURCH CUTOFF'
      ! CUTOFF IMPLEMENTATION, following burch et al. (1969) and bruno's fit: use this for CO2 only
      ! This is for broadening by H2/He
         do i = 1, n_lambda

            if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= 35d0) then
               phi_p(i) = phi_p(i)*0.03131d0*exp(-abs(1d0/lambda(i) - (1d0/lambda_eff))/87.61d0)
            else if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= 3.0d0) then
               phi_p(i) = phi_p(i)*0.1804d0*exp(-abs(1d0/lambda(i) - (1d0/lambda_eff))/16.28d0)
            else if (abs(1d0/lambda(i) - (1d0/lambda_eff)) >= 1.1d0) then
               phi_p(i) = phi_p(i)*2.5825d0*exp(-abs(1d0/lambda(i) - (1d0/lambda_eff))/1.054d0)
            end if

         end do
      else
         !write(*,*) 'No cutoff'
      end if

    end subroutine phi_prime



    subroutine calc_sigma_coarse_interpol(trans_length, w_number, gamma, sigma_D, line_int_corr, temp, pressure_atm, lambda_min, &
            resolution, n_lambda,delta_lam_steps,lambda,phi_p,sigma, no_sub_grid, sub_grid_borders, cutoff_str, cutoff, verbose)

      implicit none

      INTEGER :: i, j, m
      INTEGER,intent(in) :: trans_length

      ! trans function
      DOUBLE PRECISION,intent(in)    :: w_number(trans_length)
      DOUBLE PRECISION,intent(in)    :: line_int_corr(trans_length)
      DOUBLE PRECISION,intent(in)    :: gamma(trans_length)
      DOUBLE PRECISION,intent(in)    :: sigma_D(trans_length)

      ! Voigt interpolation

      ! input
      DOUBLE PRECISION,intent(in)    :: temp, pressure_atm, lambda_min
      DOUBLE PRECISION,intent(in)    :: resolution
      INTEGER,intent(in)    :: n_lambda
      DOUBLE PRECISION,intent(in)    :: lambda(n_lambda)
      INTEGER,intent(in) :: delta_lam_steps,no_sub_grid
      INTEGER,intent(in) :: sub_grid_borders(no_sub_grid+1)

      ! output
      DOUBLE PRECISION,intent(inout)    :: sigma(n_lambda)
      DOUBLE PRECISION,intent(out)    :: phi_p(n_lambda)

      ! control
      ! control
      LOGICAL :: calc_coarse
      DOUBLE PRECISION :: alpha_prof,gauss_contr

      ! cutoff
      CHARACTER, intent(in)  ::cutoff_str
      DOUBLE PRECISION,intent(in)  :: cutoff

      ! verbose
      LOGICAL, intent(in) :: verbose

      ! internal
      INTEGER :: offset,right_ind
      !INTEGER :: sub_grid_lines(no_sub_grid+1)
      DOUBLE PRECISION :: coarse_grid(10), pressure_enha
      DOUBLE PRECISION :: sigma_course_grid(10), phi_p_coarse(10)
      DOUBLE PRECISION :: left_border, right_border
      DOUBLE PRECISION :: sigma_ext_grid_coarse(no_sub_grid+2,10)
      DOUBLE PRECISION :: p_atm, p_shift_w_number, p_bar, pressure
      DOUBLE PRECISION :: gamma_doppler, gamma_D_dist, gamma_L_dist
      INTEGER :: sub_lum, i_lambda
      INTEGER :: left_ind, offset_left, offset_i, current_fine_ind
      DOUBLE PRECISION :: power_law_slope, mult_factor, addT,slope, meanWnumber
      DOUBLE PRECISION, allocatable :: fine_subgrid_sigma(:)
      INTEGER :: no_lines_coarse(no_sub_grid)

      pressure = pressure_atm * 1.01325d5 * 1d6  ! convert to cgs units (dyn/cm2)


      p_bar = pressure*1d-6

      pressure_enha = 1d0 + 9.9999d4 / (1d0 + exp(5d0-p_bar)/p_bar**2d0)
      alpha_prof = 1d-8*pressure_enha
      if (p_bar > 1d1) then
         alpha_prof = alpha_prof * (p_bar**2d0/1d2)
      end if

      gauss_contr = 5d3/sqrt(temp/1d2)

      !------------------------------------------------------------------------------------------
      ! Calculate sigma for all in-subgrid lines within each subgrid
      !------------------------------------------------------------------------------------------

      if (verbose) then
        write(*,*) 'Starting internal lines!'
      end if

      p_atm = pressure * 1d-6 / 1.01325d0

      ! Iterate over the subgrids
      do m = 1, no_sub_grid

         if (m == 1) then
            offset = 0
         else
            offset = 1
         end if

         offset_left = 1
         if (m == no_sub_grid) then
            offset_left = 0
         end if


            do i = 1, trans_length

                  p_shift_w_number = w_number(i)

                  if ( ((1d0/p_shift_w_number) > lambda(sub_grid_borders(m)+offset)) &
                       .AND. ((1d0/p_shift_w_number) < lambda(sub_grid_borders(m+1)+offset_left)) ) then


                     call phi_prime(gamma(i), sigma_D(i), w_number(i), &
                             lambda(sub_grid_borders(m)+offset:sub_grid_borders(m+1)), &
                             sub_grid_borders(m+1) - sub_grid_borders(m) + (1-offset), &
                             phi_p(sub_grid_borders(m)+offset:sub_grid_borders(m+1)), &
                             cutoff_str, cutoff)

                     do j = sub_grid_borders(m)+offset, sub_grid_borders(m+1)
                        sigma(j) = sigma(j) + line_int_corr(i) * phi_p(j)
                     end do

                  end if

            end do

      end do

      if (verbose) then
        write(*,*) 'Internal lines done!'
        write(*,*) 'Starting external lines!'

      end if
      !------------------------------------------------------------------------------------------
      ! Do the external line calc.
      !------------------------------------------------------------------------------------------



      ! Iterate over the subgrids
      do m = 1, no_sub_grid

         if (verbose) then
            if (mod(m, 10) == 0) then
                write(6,'(A,I0,A,I0, A)', advance='no') 'Progress: ', m, '/', no_sub_grid, ' subgrids'
                write(6,'(A)', advance='no') char(13)
                call flush(6)
            end if
         end if


         if (m == 1) then
            offset = 0
         else
            offset = 1
         end if

         offset_left = 1
         if (m == no_sub_grid) then
            offset_left = 0
         end if

         left_border = lambda(sub_grid_borders(m)+offset)
         right_border = lambda(sub_grid_borders(m+1))
         do i = 1,10

            coarse_grid(i) = left_border + (right_border-left_border)*(DBLE(i)-1d0)/9d0
            do j = 1, no_sub_grid+2

               sigma_ext_grid_coarse(j,i) = 0d0

            end do

         end do

         do i = 1, no_sub_grid

            no_lines_coarse(i) = 0

         end do

         !write(*,*) 'DEBUG', 1

            do i = 1, trans_length

                  !write(*,*) 'DEBUG', 2

                  ! NO pressure shift anymore!
                  p_shift_w_number = w_number(i) !+del_ref(i)*p_atm

                  ! is the line outside the subgrid m
                  if ( ((1d0/p_shift_w_number) < lambda(sub_grid_borders(m)+offset)) &
                       .or. ((1d0/p_shift_w_number) > lambda(sub_grid_borders(m+1)+offset_left)) ) then ! + 1 behin (m+1) is new

                     i_lambda = IDINT(dlog(1d0/p_shift_w_number/lambda_min)*resolution)+1
                     ! is the line inside the total grid?
                     if (i_lambda >= 1 .AND. i_lambda <= n_lambda) then

                        !write(*,*) 'DEBUG', 3, 'a'

                        ! get in which subgrid the line is
                        sub_lum = i_lambda / delta_lam_steps + 1
                        if (modulo(i_lambda,delta_lam_steps) == 0) then
                           sub_lum = sub_lum - 1
                        end if

                        no_lines_coarse(sub_lum) = no_lines_coarse(sub_lum)+1

                        ! gamma Doppler
                        gamma_doppler = sigma_D(i) * sqrt(2d0)

                        gamma_D_dist = min(abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m)+offset))/gamma_doppler, &
                             abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m+1)+offset_left))/gamma_doppler)

                        gamma_L_dist = min(abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m)+offset))/gamma(i), &
                             abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m+1)+offset_left))/gamma(i))

                        if (gamma_doppler > gamma(i)) then
                           if (gamma_D_dist < gauss_contr) then
                              calc_coarse = .False.
                           else if (gamma_L_dist < 1d0/sqrt(alpha_prof)) then
                              calc_coarse = .False.
                           else
                              calc_coarse = .True.
                           end if
                        else
                           if (gamma_L_dist < 1d0/sqrt(alpha_prof)) then
                              calc_coarse = .False.
                           else
                              calc_coarse = .True.
                           end if
                        end if

                        if (sub_lum == m) then
                           calc_coarse = .False.
                        end if

                        ! if too close: consider at all subgrid points.
                        if (.not. calc_coarse) then

                           call phi_prime(gamma(i), sigma_D(i), w_number(i), &
                                   lambda(sub_grid_borders(m)+offset:sub_grid_borders(m+1)), &
                                   sub_grid_borders(m+1) - sub_grid_borders(m) + (1-offset), &
                                   phi_p(sub_grid_borders(m)+offset:sub_grid_borders(m+1)),&
                                   cutoff_str,cutoff)

                           do j = sub_grid_borders(m)+offset, sub_grid_borders(m+1)
                              sigma(j) = sigma(j) + line_int_corr(i) * phi_p(j)
                           end do
                        ! Else: do the coarse calculation.
                        else

                           ! Set the sigma for that line to 0.
                           do j = 1, 10
                              sigma_course_grid(j) = 0d0
                           end do

                           ! calculate the coarse grid line prof.
                           call phi_prime(gamma(i), sigma_D(i), w_number(i), &
                                   coarse_grid, 10, phi_p_coarse, cutoff_str,cutoff)

                           do j = 1, 10
                              sigma_course_grid(j) = sigma_course_grid(j) + line_int_corr(i) * phi_p_coarse(j)
                           end do

                           ! add to the total coarse grid array for this particular subgrid
                           sigma_ext_grid_coarse(sub_lum,:) = sigma_ext_grid_coarse(sub_lum,:) + sigma_course_grid

                        ! end if fine or coarse grid calc
                        end if

                     ! else: line outside of total grid
                     else

                        !write(*,*) 'DEBUG', 3, 'b'

                        ! get in which subgrid the line is
                        if (1d0/p_shift_w_number < lambda(1)) then
                           ! left of total grid
                           sub_lum = no_sub_grid+1
                        else
                           ! right of total grid
                           sub_lum = no_sub_grid+2
                        end if

                        ! calculate the gammas
                        ! call amu_mass(file_str,iso_arr(i),amu_m)
                        ! gamma Lorentz
                        !gamma = (t_ref/temp)**n_temp(i) * ( gamma_medium(i) * (p_atm - part_press) + gamma_self(i) * part_press )
                        !gamma = gamma + einstein_a(i)/c/4d0/pi

                        ! gamma Doppler
                        gamma_doppler = sigma_D(i) * sqrt(2d0)

                        gamma_D_dist = min(abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m)+offset))/gamma_doppler, &
                             abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m+1)+offset_left))/gamma_doppler)

                        gamma_L_dist = min(abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m)+offset))/gamma(i), &
                             abs(p_shift_w_number-1d0/lambda(sub_grid_borders(m+1)+offset_left))/gamma(i))

                        if (gamma_doppler > gamma(i)) then
                           if (gamma_D_dist < gauss_contr) then
                              calc_coarse = .False.
                           else if (gamma_L_dist < 1d0/sqrt(alpha_prof)) then
                              calc_coarse = .False.
                           else
                              calc_coarse = .True.
                           end if
                        else
                           if (gamma_L_dist < 1d0/sqrt(alpha_prof)) then
                              calc_coarse = .False.
                           else
                              calc_coarse = .True.
                           end if
                        end if

                        ! if too close: consider at all subgrid points.
                        if (.not. calc_coarse) then

                           !write(*,*) 'DEBUG', 5, 'a'

                           call phi_prime(gamma(i), sigma_D(i), w_number(i), &
                                   lambda(sub_grid_borders(m)+offset:sub_grid_borders(m+1)), &
                                   sub_grid_borders(m+1) - sub_grid_borders(m) + (1-offset), &
                                   phi_p(sub_grid_borders(m)+offset:sub_grid_borders(m+1)),&
                                   cutoff_str,cutoff)

                           do j = sub_grid_borders(m)+offset, sub_grid_borders(m+1)
                              sigma(j) = sigma(j) + line_int_corr(i) * phi_p(j)
                           end do
                           ! Else: do the coarse calculation.
                        else

                           !write(*,*) 'DEBUG', 5, 'b'

                           ! Set the sigma for that line to 0.
                           do j = 1, 10
                              sigma_course_grid(j) = 0d0
                           end do

                           !write(*,*) 'DEBUG', 6

                           ! calculate the coarse grid line prof.
                           call phi_prime(gamma(i), sigma_D(i), w_number(i), coarse_grid, 10, phi_p_coarse, &
                                   cutoff_str, cutoff)

                           !write(*,*) 'DEBUG', 7

                           do j = 1, 10
                              sigma_course_grid(j) = sigma_course_grid(j) + line_int_corr(i) * phi_p_coarse(j)
                           end do

                           !write(*,*) 'DEBUG', 8

                           ! add to the total coarse grid array for this particular subgrid
                           sigma_ext_grid_coarse(sub_lum,:) = sigma_ext_grid_coarse(sub_lum,:) + sigma_course_grid

                        end if

                        !write(*,*) 'DEBUG', 9

                     ! end if in or out of total grid
                     end if

                  ! end if line outside of grid
                  end if

            ! end loop over all transitions
            end do

         !------------------------------------------------------------------------------------------
         ! Do the powerlaw interpolation
         !------------------------------------------------------------------------------------------

         do i = 1,10
            sigma_course_grid(i) = 0
         end do

         do i = 1, no_sub_grid+2
            if (i /= m) then
               sigma_course_grid = sigma_course_grid + sigma_ext_grid_coarse(i,:)
            end if
         end  do

         sigma(sub_grid_borders(m)+offset) = sigma(sub_grid_borders(m)+offset) + sigma_course_grid(1)
         sigma(sub_grid_borders(m+1)) = sigma(sub_grid_borders(m+1)) + sigma_course_grid(10)


         allocate(fine_subgrid_sigma((sub_grid_borders(m+1)-1)-(sub_grid_borders(m)+offset+1)+1))
         do i = 1, (sub_grid_borders(m+1)-1)-(sub_grid_borders(m)+offset+1)+1
            fine_subgrid_sigma(i) = 0d0
         end do

         do i = 1, no_sub_grid + 2

            if (i /= m .AND. i <= no_sub_grid .AND. no_lines_coarse(i) /= 0) then

               if (i == 1) then
                  offset_i = 0
               else
                  offset_i = 1
               end if

               meanWnumber = (1d0/lambda(sub_grid_borders(i)+offset_i)+1d0/lambda(sub_grid_borders(i+1)))/2d0

               ! interpolate the rest
               left_ind = 9
               if (sigma_ext_grid_coarse(i,left_ind) > 1d-50 .AND. sigma_ext_grid_coarse(i,left_ind+1) > 1d-50) then
                  power_law_slope = DLOG(sigma_ext_grid_coarse(i,left_ind))-DLOG(sigma_ext_grid_coarse(i,left_ind+1))
                  power_law_slope = power_law_slope / (DLOG(abs(1d0/coarse_grid(left_ind)-meanWnumber)) &
                       -DLOG(abs(1d0/coarse_grid(left_ind+1)-meanWnumber)))
                  mult_factor = sigma_ext_grid_coarse(i,left_ind)/(abs(1d0/coarse_grid(left_ind)-meanWnumber))**power_law_slope
               else
                  power_law_slope = 1d0
                  mult_factor = 0d0
               end if

               current_fine_ind = (sub_grid_borders(m+1)-1)-(sub_grid_borders(m)+offset+1)+1+1
               do j = (sub_grid_borders(m+1)-1),(sub_grid_borders(m)+offset+1),-1
                  current_fine_ind = current_fine_ind - 1
                  if (1d0/lambda(j) > 1d0/coarse_grid(left_ind)) then
                     left_ind = left_ind-1
                     if (sigma_ext_grid_coarse(i,left_ind) > 1d-50 .AND. sigma_ext_grid_coarse(i,left_ind+1) > 1d-50) then
                        power_law_slope = DLOG(sigma_ext_grid_coarse(i,left_ind))-DLOG(sigma_ext_grid_coarse(i,left_ind+1))
                        power_law_slope = power_law_slope / (DLOG(abs(1d0/coarse_grid(left_ind)-meanWnumber)) &
                             -DLOG(abs(1d0/coarse_grid(left_ind+1)-meanWnumber)))
                        mult_factor = sigma_ext_grid_coarse(i,left_ind)/(abs(1d0/coarse_grid(left_ind)-meanWnumber))**power_law_slope
                     else
                        power_law_slope = 1d0
                        mult_factor = 0d0
                     end if
                  end if

                  addT = mult_factor * (abs(1d0/lambda(j)-meanWnumber))**power_law_slope

                  if (addT == addT) then
                     if (addT > 1d300) then
                        !write(*,*) 'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL'
                     else
                        fine_subgrid_sigma(current_fine_ind) = fine_subgrid_sigma(current_fine_ind) + addT
                     end if
                  end if
               end do
            else if (i > no_sub_grid) then

            ! interpolate linearly outside of the total grid
            right_ind = 2
            slope = (sigma_ext_grid_coarse(i,right_ind)-sigma_ext_grid_coarse(i,right_ind-1))
            slope = slope/(coarse_grid(right_ind)-coarse_grid(right_ind-1))
            do j = (sub_grid_borders(m)+offset+1),(sub_grid_borders(m+1)-1)
               if (lambda(j) > coarse_grid(right_ind)) then
                  right_ind = right_ind+1
                  slope = (sigma_ext_grid_coarse(i,right_ind)-sigma_ext_grid_coarse(i,right_ind-1))
                  slope = slope/(coarse_grid(right_ind)-coarse_grid(right_ind-1))
               end if
               sigma(j) = sigma(j) + sigma_ext_grid_coarse(i,right_ind-1) + slope*(lambda(j)-coarse_grid(right_ind-1))
            end do

            end if

         end do
    !!$
         sigma(sub_grid_borders(m)+offset+1:sub_grid_borders(m+1)-1) = sigma(sub_grid_borders(m)+offset+1:sub_grid_borders(m+1)-1) &
              + fine_subgrid_sigma
    !!$
    !!$  ! end do over all subgrids
    !!$
         if (allocated(fine_subgrid_sigma)) deallocate(fine_subgrid_sigma)

      end do

      if (verbose) then
          write(6,*)
          write(*,*) 'External lines done!'
      end if

    end subroutine calc_sigma_coarse_interpol

    subroutine HUMLICEK(NX, X, Y, PRBFCT)
        implicit none

        ! Input arguments
        integer, intent(in) :: NX
        real(8), intent(in) :: X(0:NX)
        real(8), intent(in) :: Y

        ! Output argument
        complex(8), intent(out) :: PRBFCT(0:NX)

        ! Local variables
        integer :: I
        real(8) :: S, AX
        complex(8) :: T, U

        if (Y > 15.d0) then
            do I = 0, NX
                T = CMPLX(Y, -X(I), KIND=8)
                PRBFCT(I) = APPROX1(T)
            end do

        else if (Y < 15.d0 .and. Y >= 5.5d0) then
            do I = 0, NX
                T = CMPLX(Y, -X(I), KIND=8)
                S = ABS(X(I)) + Y
                if (S >= 15.d0) then
                    PRBFCT(I) = APPROX1(T)
                else
                    U = T*T
                    PRBFCT(I) = APPROX2(T,U)
                end if
            end do

        else if (Y < 5.5d0 .and. Y > 0.75d0) then
            do I = 0, NX
                T = CMPLX(Y, -X(I), KIND=8)
                S = ABS(X(I)) + Y
                if (S >= 15.d0) then
                    PRBFCT(I) = APPROX1(T)
                else if (S < 5.5d0) then
                    PRBFCT(I) = APPROX3(T)
                else
                    U = T*T
                    PRBFCT(I) = APPROX2(T,U)
                end if
            end do

        else
            do I = 0, NX
                T = CMPLX(Y, -X(I), KIND=8)
                AX = ABS(X(I))
                S = AX + Y
                if (S >= 15.d0) then
                    PRBFCT(I) = APPROX1(T)
                else if (S < 15.d0 .and. S >= 5.5d0) then
                    U = T*T
                    PRBFCT(I) = APPROX2(T,U)
                else if (S < 5.5d0 .and. Y >= 0.195d0*AX-0.176d0) then
                    PRBFCT(I) = APPROX3(T)
                else
                    U = T*T
                    PRBFCT(I) = CDEXP(U) - APPROX4(T,U)
                end if
            end do
        end if

        ! Handle special case Y == 0
        if (Y == 0.d0) then
            do I = 0, NX
                PRBFCT(I) = CMPLX(EXP(-X(I)**2), AIMAG(PRBFCT(I)), KIND=8)
            end do
        end if

        contains

        function APPROX1(T) result(res)
            complex(8), intent(in) :: T
            complex(8) :: res
            res = (T * 0.5641896d0) / (0.5d0 + (T * T))
        end function APPROX1

        function APPROX2(T,U) result(res)
            complex(8), intent(in) :: T,U
            complex(8) :: res
            res = (T * (1.410474d0 + U * 0.5641896d0)) / (0.75d0 + U * (3.d0 + U))
        end function APPROX2

        function APPROX3(T) result(res)
            complex(8), intent(in) :: T
            complex(8) :: res
            res = (16.4955d0 + T * (20.20933d0 + T * (11.96482d0 + T * (3.778987d0 + 0.5642236d0*T)))) &
                  / (16.4955d0 + T * (38.82363d0 + T * (39.27121d0 + T * (21.69274d0 + T * (6.699398d0 + T)))))
        end function APPROX3

        function APPROX4(T,U) result(res)
            complex(8), intent(in) :: T,U
            complex(8) :: res
            res = (T * (36183.31d0 - U * (3321.99d0 - U * (1540.787d0 - U * (219.031d0 - U * (35.7668d0 - &
                    U * (1.320522d0 - U * 0.56419d0))))))) &
                  / (32066.6d0 - U * (24322.8d0 - U * (9022.23d0 - U * (2186.18d0 - U * (364.219d0 - &
                    U * (61.5704d0 - U * (1.84144d0 - U)))))))
        end function APPROX4

    end subroutine HUMLICEK

end module line_calculation_molliere2015