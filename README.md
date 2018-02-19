### deep-murasaki

Deep learning chess engine, that has no idea about chess rules, but watches and learns.

Heavily based on [deep-pink](https://github.com/erikbern/deep-pink) by [Erik Bernhardsson](http://erikbern.com). The main idea was to improve the network configuration from 3 very costly (in terms of memory size and training time) FC layers to multiple less connected layers, that could give same or better results using only a fraction of memory and could converge during the trained much faster.

Could have started from the scratch, but too buzy/lazy to reimplement chess framework for the move generation and evaluation myself, especially when it's already done and generously given to the open source (Thanks, Eric!).

There's no pretrained model in the repository, because the model configuration still has not been firmly decided. Training is a three step process:

1. use `parse_game.py` on a bunch of .PGN formatted games to extract the data and save the results in HDF5 format.
2. use `train.py` to learn from the saved data as much as possible (GPU is a must for this step).
3. (optionally) use `reinforcement.py` to learn while playing against another chess program (sunfish).

### The requirements

* [Keras] (http://keras.io/) `sudo pip install keras`, that gives us a choice to use Theano or TensorFlow as a backend. I used Theano, if you prefer TensorFlow, there's [backend configuration guide](http://keras.io/backend/)
* [Theano](https://github.com/Theano/Theano): `git clone https://github.com/Theano/Theano; cd Theano; python setup.py install` to get the newest version, old versions have various compatibility issues and the latest available on PIP is 0.7 (quite dated).
* [Sunfish](https://github.com/thomasahle/sunfish): `git clone https://github.com/thomasahle/sunfish`. I have already included `sunfish.py` in this project, but you might want to get the newer version.
* [python-chess](https://pypi.python.org/pypi/python-chess) `pip install python-chess`
* [scikit-learn](http://scikit-learn.org/stable/install.html) (only needed for training)
* [h5py](http://www.h5py.org/): can be installed using `apt-get install python-hdf5` or `pip install hdf5` (only needed for training)
* A relatively recent NVidia card, the bigger the better. Training could be a major pain without it.
# chess-self-play
