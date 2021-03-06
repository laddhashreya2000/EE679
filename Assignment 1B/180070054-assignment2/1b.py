# -*- coding: utf-8 -*-
"""Copy of EE679_1b.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tINW12bunqtkbVKDxDyMjHfUOdeEYNu7

Assignment 1b EE679

Shreya Laddha

Roll number - 180070054
"""

import numpy as np
from scipy.signal import zpk2tf,square
from scipy.fft import fft,fftfreq
from math import pi
from numpy import exp,zeros_like,log10,hamming
from numpy import convolve as conv
import matplotlib
import pylab as plt
from scipy import signal
from math import pi
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

def get_audio_waveform(f0, f1, f2, f3): ##taken from assignment 1
  #other parameters
  b1 = 100
  fs = 16000
  ts = 1/fs
  T = 0.5
  num_samples = int(fs*T)

  #getting transfer function for each frequency as a single formant resonator
  r = np.exp(-pi*b1*ts)
  theta = [2*pi*f1*ts, 2*pi*f2*ts, 2*pi*f3*ts]
  num1, den1 = signal.zpk2tf([0,0], [r*np.exp(1j*theta[0]) , r*np.exp(-1j*theta[0])], 1)
  num2, den2 = signal.zpk2tf([0,0], [r*np.exp(1j*theta[1]) , r*np.exp(-1j*theta[1])], 1)
  num3, den3 = signal.zpk2tf([0,0], [r*np.exp(1j*theta[2]) , r*np.exp(-1j*theta[2])], 1)

  #for plotting magnitude response combine all poles and zeroes to get single transfer function of the cascade
  poles = [r*np.exp(1j*theta[0]) , r*np.exp(-1j*theta[0]), r*np.exp(1j*theta[1]) , r*np.exp(-1j*theta[1]), r*np.exp(1j*theta[2]) , r*np.exp(-1j*theta[2])]
  zeros = [0,0,0,0,0,0]
  num, den = signal.zpk2tf(zeros, poles, 1)
  
  #Plotting magnitude response
  omega, freq_resp = signal.freqz(num, den)
  # plt.figure()
  # plt.title('Filter magnitude response for '+phone+' at f0 = '+str(f0)+' Hz')
  f_hz = fs * omega/(2*pi)
  mag = 20*np.log10(abs(freq_resp))
  # plt.plot(f_hz,mag,'b')
  # plt.ylabel('Amplitude in dB')
  # plt.xlabel('Frequency in Hz')
  # plt.show()


  time = np.linspace(0, T, num_samples)
  x = np.zeros(num_samples)
  y = np.zeros(num_samples)
  state1 = np.zeros(num_samples)
  state2 = np.zeros(num_samples)

  #Impulse train
  for i in range(0, int(T*f0)):
    x[i*int(np.floor(fs/f0))] = 1

  #using differnce equations - since there are three cascade systems for three different formant freq, have to do three times
  #first system
  state1[0] = x[0]
  state1[1] = x[1] - den1[1].real*state1[0]	
  for i in range(2, num_samples):
      state1[i] = x[i] - den1[1].real*state1[i-1] - den1[2].real*state1[i-2]

  #second system
  state2[0] = state1[0]
  state2[1] = state1[1] - den2[1].real*state2[0]	
  for i in range(2, num_samples):
      state2[i] = state1[i] - den2[1].real*state2[i-1] - den2[2].real*state2[i-2]
  
  #Last third system
  y[0] = state2[0]
  y[1] = state2[1] - den3[1].real*y[0]	
  for i in range(2, num_samples):
      y[i] = state2[i] - den3[1].real*y[i-1] - den3[2].real*y[i-2]

  # #plotting outputs
  # plt.figure()
  # plt.title('Excitation Response for '+phone+' at f0 = '+str(f0)+' Hz')
  # plt.plot(time, y, 'b')
  # plt.ylabel('Amplitude')
  # plt.xlabel('Time in sec')
  # plt.show()

  # plt.figure()
  # plt.title('Excitation Response Zoomed in for '+phone+' at f0 = '+str(f0)+' Hz')
  # plt.plot(time[0:1000], y[0:1000], 'b')
  # plt.ylabel('Amplitude')
  # plt.xlabel('Time in sec')
  # plt.show()
  # y = np.int16(y/np.max(np.abs(y))*32767)
  # write("audio_'"+phone[1]+"'_"+str(f0)+"Hz.wav",16000,y)
	
  return y

def get_window(window, win_length,fs,output,f0):
  window_size = int(win_length*fs/1000)
  if(window=='Hamming'):
    window_signal = output[:window_size] * hamming(window_size)
  else:
    window_signal = output[:window_size]
  dft = fft(window_signal, n=1024)
  freq = fftfreq(dft.shape[-1], 1/fs)

  plt.figure()
  
  plt.plot(abs(freq),20*log10(abs(dft)),'b')
  plt.xlim(xmin=0)
  plt.grid("True")
  plt.title("{} Window response for length {}ms with signal freq {}Hz".format(window, win_length,f0))
  plt.ylabel(r"$|H(\Omega|$")
  plt.xlabel(r"$\Omega$")
  plt.savefig("./plots/"+window+"_Window_Freq_resp_"+str(f0)+"_"+str(win_length)+".png")
  plt.show()
  # plt.figure()
  # plt.plot(abs(freq[:200]),20*log10(abs(dft[:200])),'r') #magnified plot for F0 calculation
  # plt.title("{} Window Magnified response for length {}ms with signal freq {}Hz".format(window, win_length,f0))
  # plt.ylabel(r"$|H(\Omega|$")
  # plt.xlabel(r"$\Omega$")
  #not saving this plot

def generate_vowels(formant_frequencies,bandwidth,signal_frequency,time,fs,window,win_length):
  f1 = formant_frequencies[0]
  f2 = formant_frequencies[1]
  f3 =formant_frequencies[2]

  response = get_audio_waveform(signal_frequency, f1,f2,f3)
  # get DFT and plot
  get_window(window, win_length,fs,response,signal_frequency)

f0 = [120,220]
formant_freq = [300,870,2240]
time = 0.5
fs = 16000
bw = 100
windows = ["Hamming","Rectangular"]
window_lengths = [5,10,20,40]

for freq in f0:
  for window in windows:
    for win_length in window_lengths:
      generate_vowels(formant_freq,bw,freq,time,fs,window,win_length)
      # break

