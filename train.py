import neurolab
import numpy

import features
import models

input_range = [0, 1]
all_features = features.BaseFeature.registry.values()
net = neurolab.net.newff(
    [input_range] * len(all_features),
    [2 * len(all_features), 3]
)

# parse data
models.Tournament.get_all()

game_features, results = map(numpy.array, models.Game.get_training_examples())
print 'Fetched {} data rows, start learning'.format(len(game_features))
err = net.train(game_features, results, show=20)
