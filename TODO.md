## First
- Better refactory of volume system

## Octave extension
- Add "interval extension" to define an octave extension (settings and implementation)

## Oscillators
- Define common oscillators
- Maybe we should not differenciate between oscillators and signals! One could define a subclass FunctionSignal <: Signal to make a signal out of a generating function.
- Make generator of signals/oscillators with parametric frequences. I.E. write osc = Sin() or osc = SawTooth() and then call osc(freq) to return an actual oscillator (good idea?)

## "GUI"
- show exactly one period (440Hz or base note) on the oscilloscope view?
