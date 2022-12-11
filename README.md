Esta libreria permite calcular entropia en 3 dimensiones en varias escalas.
This library allows to calculate MSE in three dimensions.

Ejemplo/Example: 

entropy_values = entropy_3D.mse_entropy_3d('test_data/white_noise_1.mp4', scales=10, m=2, r=0.2)

Como regla general, si input = (video de 10 segundos, resolucion de 500x500 pixeles),
se va a demorar 20 minutos en calcular. 

As a general rule, if input = (10 second video, resolution 500x500), it will take 20 minutes
to calculate.

Casos Bases/Base Cases.

Abajo grafico que representa casos bases.
Below a plot that represents the base cases.

('white_noise_generated' = video en donde cada pixel es una serie de tiempo con ruido blanco, 
el resto son videos sacados de youtube.)
('white_noise_generated' = video where each pixel is a time series with white noise, the rest
are videos from youtube.)

