

class EvenSeq(object):

    def __init__(self, to_num: int, min_len: int = 0, dict_list: bool = True):
        """
        It is responsible for the dictionary with the sequences.
        
        i.e.
        self.to_dict: {2: [2, 4, 8, 16, 14, 10, 2], ... }
        
        :param to_num: up to which number the dict will be
        
        :param min_len: minimum length of each sequence in the dictionary.
                        EXAMPLE
                        in:     min_len < 8
                        out:    2: [2, 4, 8, 16, 14, 10, 2], ...
                        in:     min_len < 16
                        out:    2: [2, 4, 8, 16, 14, 10, 2, 4, 8, 16, 14, 10, 2], ...
                        
        :param dict_list: whether the dict will contain
                          lists or generators with the lists
        
        """
        
        self.r = range(to_num+1)
        self.m = min_len
        self.c = dict_list

    def non_repetitive(func):
        """
        self.sequence Decorator

        :return: sequence of the given number until it
                 finds a num that is already in the sequence
                 i.e. to create list patterns
        """
        def wrapper(self, n: int):
            lst = list()
            while n not in lst:
                lst.append(n)
                n = func(self, n)
                yield n
        return wrapper

    def extender(func):
        """
        self.sequence Decorator
        
        :return: it extends according to min_len
        """
        def wrapper(self, n: int):
            seq = list(func(self, n))
            if self.m > len(seq):
                from math import ceil

                def len_fn(i):
                    return ceil(self.m / (len(seq)-i))

                n_next = self.formula(seq[-1])
                if n is seq[-1] or seq[0] is n_next:
                    seq = [*seq * len_fn(0)]
                elif seq[0] is seq[-1]:
                    seq = [*seq[1:] * len_fn(1)]

            return seq
        return wrapper

    @staticmethod
    def formula(n: int):
        """
        computes the formula
        
        :param n: int
        """
        return 2 * sum((int(i) for i in str(n)))

    @extender
    @non_repetitive
    def sequence(self, n: int):
        """
        Returns the sequence of a given number
        """
        return self.formula(n)

    def _lst(self, func):
        """
        changes dict to iterator according to dict_list
        """
        if self.c:
            return func
        else:
            return iter(func)

    @property
    def to_dict(self):
        """
        :return: dictionary from 0 to to_num var
        """
        def mapper(x):
            if x > 1:
                return x, self._lst(self.sequence(x))
            else:
                return x, [0]
        return dict(map(mapper, self.r))

    @property
    def seq_last(self):
        """
        :return: gives the last number of each seq
        """
        def mapper(x):
            if x > 1:
                return self.sequence(x)[-1]
            else:
                return 0
        return list(map(mapper, self.r))

    @property
    def seq_len(self):
        """
        :return: gives the len of each seq
        """
        def mapper(x):
            if x > 1:
                return len(self.sequence(x))
            else:
                return 0
        return list(map(mapper, self.r))


class Sequencer(EvenSeq):

    def __init__(self, init_n: int, limit: int, *args, **kwargs):
        """
        Class to compute the sequence or partition it if needed
        
        :param init_n: initial number
        :param limit: rough length of the sequence
        :param args: params of EvenSeq
        :param kwargs: params of EvenSeq
        """
        
        if kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(20)

        self.dct = self.to_dict
        self.lst = self.seq_last
        self.lng = self.seq_len
        self.lim = limit

        self.n = init_n

    def yield_sequence(self):
        """
        yields the sequence of
            length: param limit
            init: param number
        """
        n = self.n
        m = self.lim
        yield n

        while m > 0:
            if n in self.dct.keys():

                if n is self.lst[n]:
                    from math import ceil

                    r = ceil(m/self.lng[n])
                    for _ in range(r):
                        yield self.dct[n]
                    break
                else:
                    m = m - self.lng[n]
                    n = self.lst[n]
                    yield self.dct[n]

            else:
                n = self.formula(n)
                m = m - 1
                yield n

    def _partition(self, s, m):
        """
        yields a partition of yield_sequence
        
        :param s: sequence iterator
        :param m: maximum number of lists/iterators per partition
        :return: 1 partition
        """
        if m:
            try:
                yield next(s)
                yield from self._partition(s, m - 1)
            except StopIteration as e:
                pass

    def partitioner(self, s, m):
        """
        repartitions the sequence by combining lists/generators
        :param s: sequence
        :param m: maximum lists/generators per partition
        :return: generator of generators
        """
        from itertools import chain

        while True:
            new = list(self._partition(s, m))
            if new:
                yield chain(*new)
            else:
                break

    @property
    def element_length(self):
        """
        total number of lists in the sequence
        if extender is used it approximately computes
        the length of total elements by:
        self.element_length * min_len
        """
        s = self.yield_sequence()
        return sum(map(lambda x: 1, s))


if __name__ == '__main__':
    """ Some instructions before you run it """
    # min_len needs tuning according to your ram memory.
    # You can tune it by using timeit package and try different
    # combinations and check when it takes long to produce a dict
    # I give an example below for tuning.
    # As a rule of thumb, minimum len should be less or equal with
    # the limit.
    # 
    # from timeit import default_timer
    # 
    # for exponent in range(1, 8):
    #     starting_time = default_timer()
    #     Cls = Sequencer(init_n=2, limit=1, to_num=20,
    #                     min_len=10 ** exponent)
    #     k = Cls.to_dict
    #     print(default_timer() - starting_time)
    # ------------------------------------------------------------
    # 
    # Test much time it takes to retrieve the numbers with the following:
    # 
    # from timeit import default_timer
    # 
    # Cls = Sequencer(init_n=2, limit=10**8,
    #                 to_num=20, min_len=10**4)
    # 
    # starting_time = default_timer()
    # 
    # my_sequence = Cls.yield_sequence()
    # for _ in my_sequence:
    #     pass
    # 
    # print(default_timer() - starting_time)
    # ------------------------------------------------------------
    # 
    # CAREFUL
    # The sequence always starts with the initial number
    # and then continues with lists/generators
    
    Cls = Sequencer(init_n=2, limit=10**100,
                    to_num=20, min_len=10**5, dict_list=True)  # kwargs from EvenSeq class
    
    my_sequence = Cls.yield_sequence()
