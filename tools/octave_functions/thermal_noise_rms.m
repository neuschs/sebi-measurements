function noise = thermal_noise_rms(noise_density_hz, f1, f2)
  % noise density @ 1hz is the input parameter
  noise = noise_density_hz * sqrt(log(f2 / f1));
endfunction