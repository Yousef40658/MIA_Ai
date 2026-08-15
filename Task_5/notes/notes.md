# Stanford EE368/CS232
## Introduction
### Image
image is a visual representation in a form of a function f(x,y) where f is related to the brightness or color at point (x,y).
an image is continuos in amplitude and space

### Digital Image 
since continuos signals can't be used in computers , images were discretized using pixels. with the same methodology as normal sampling, using too many pixels will result in over-sampling -capturing unnecessary details- , using too few pixels will result in under-sampling omitting important data 

each pixel is represented by (x,y) where x,y are the corresponding row and col indices. - (0,0) is top left

### Color Components 
since each color consists of a combination of Red,Green and Blue .
cameras can be set in the same to construct 3 RGB channels with each having it's individual brightness/value .
when the 3 channels are combined you create the image with it's details again
![alt text](image.png) [RGB]
or
![alt text](image-1.png)[HSV]
where (H)ue is the color itself . measured from 0 to 360(continuos)
![alt text](image-2.png)
(S)aturation is how intense/pure this color is 
(V)alue is how bright or dark the color is

## Point Operations 
### Quantization 
after sampling you break the image into pixels but each pixel still holds a continuos value.
quantization is taking the infinitely continuos values for a pixel and mapping it to a limited number of discrete levels .
**Continuous image** —*Sampling*→ **Discrete pixels** —*Quantization*→ **Discrete pixel values**
a 8bit image will have pixel values ranging between 0 and 255 .
the higher the n of bits , the better the description of the continuos value but the higher the size .
![alt text](image-3.png)

._. okay the course got weird with over mathematics , let's check extra resources.

# Signal Processing Session Extra Knowledge 
## Quantization Error
the error introduces when we convert the continuos amplitude signal into a digital signal with a limited number of amplitude levels.
for ex if you've ac continuos signal that ranges from 0 to 9K
if you describe it using 100 amplitude levels(i know it should be 2^^n but just for example) where each level is 0.09k.
to describe the 0.12k frequency the closest option would be the first level with 0.09k with an error of 0.03k

as you increase the n of bits representing the signal you could describe numbers accurately and this quantization error decreases 

- Standard FFT assumes stationary , and fails for a non-stationary signal so STFT is used instead 

![alt text](image-4.png)
# 3Blue1Brown FT

     
