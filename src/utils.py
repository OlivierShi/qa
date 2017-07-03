# -*- coding: utf-8 -*-
import numpy as np
import cPickle as pkl
import jieba
import random
from config.conf import *


def save_model(filename, model):
    ps = {}
    for p in model.params:
        ps[p.name] = p.get_value()
    pkl.dump(ps, open(filename, 'wb'))


def load_model(filename, model):
    ps = pkl.load(open(filename, 'rb'))
    for p in model.params:
        if p not in ps:
            raise Warning('%s is not in the archive...' % p)
        p.set_value(ps[p.name])
    return model


class PrepareData():
    def __init__(self, filename, test_size=0, valid_size=0):
        self.test_size = test_size
        self.valid_size = valid_size
        with open(filename, 'r') as f:
            self.documents = f.readlines()

    def build_vocab(self):
        print "data_utils.PrepareData.build_vocab: running..."
        vocab = {}
        sources = []
        targets = []
        is_question = True
        for line in self.documents:
            line = line.replace('\n', '')
            if use_jieba:
                words = jieba.cut(line)
            else:
                words = line.decode('utf-8').strip().split()
            line2idx = []
            if is_question:
                for word in words:
                    try:
                        line2idx.append(vocab[word])
                    except:
                        vocab[word] = len(vocab)
                        line2idx.append(vocab[word])
                sources.append(line2idx)
                is_question = False
            else:
                for word in words:
                    try:
                        line2idx.append(vocab[word])
                    except:
                        vocab[word] = len(vocab)
                        line2idx.append(vocab[word])
                targets.append(line2idx)
                is_question = True
        return sources, targets, vocab

    def load_data(self):
        print "data_utils.PrepareData.load_data: running..."
        try:
            with open(vocabPath, 'rb') as f:
                self.vocab = pkl.load(f)
            with open(dataPkl, 'rb') as f:
                self.sources, self.targets = pkl.load(f)
            print "loading data from save path..."
        except:
            s, t, self.vocab = self.build_vocab()
            indexs = range(len(s))
            random.shuffle(indexs)
            self.sources = [s[i] for i in indexs]
            self.targets = [t[i] for i in indexs]
            with open(vocabPath, 'w') as f:
                pkl.dump(self.vocab, f)
            with open(dataPkl, 'w') as f:
                pkl.dump((self.sources, self.targets), f)
            print "loading data from corpus and save to save path..."

    def get_train(self):
        s = np.array(self.sources)
        t = np.array(self.targets)
        print "shape of questions: ", s.shape
        print "shape of answers: ", t.shape
        return self.sources[0: -self.test_size-self.valid_size], self.targets[0: -self.test_size-self.valid_size]

    def get_test(self):
        return self.sources[-self.test_size:], self.targets[-self.test_size:]

    def get_valid(self):
        return self.sources[-self.test_size-self.valid_size: -self.test_size], \
               self.targets[-self.test_size-self.valid_size: -self.test_size]


def reformat_data(seqs):
    lengths = [len(s) for s in seqs]
    n_samples = len(seqs)
    maxlen = np.max(lengths)
    x = np.zeros((maxlen, n_samples)).astype('int32')
    x_mask = np.zeros((maxlen, n_samples)).astype('float32')
    for idx, s in enumerate(seqs):
        x[: lengths[idx], idx] = s[::]
        x_mask[: lengths[idx], idx] = 1
    return x, x_mask


if __name__=="__main__":
    # path = '../data/webqa/qa_pairs.txt'
    # data_loader = PrepareData(path, test_size)
    # data_loader.load_data()
    # vocab = data_loader.vocab
    # vocab_size = len(vocab)
    # print vocab_size

    # reformat data
    seqs = [[23, 44, 1, 95], [43, 55]]
    x, m = reformat_data(seqs)
    print x
    print x.shape
    print m