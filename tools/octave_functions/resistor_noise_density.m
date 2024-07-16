function noise = resistor_noise_density(resistance, temperature = 25.0)
  % resistor noise
  boltzmann = physical_constant("Boltzmann constant");
  temperature_k = temperature + 273.15;
  noise = sqrt(4 * boltzmann * temperature_k * resistance);
endfunction