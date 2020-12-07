from itertools import tee


class _Dictionary(object):

    def __init__(self, to_num: int, min_len: int = 0):
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
        self.max_key = to_num
        self.r = range(to_num + 1)
        self.m = min_len

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
                    return ceil(self.m / (len(seq) - i))

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
    def __seq__(self, n: int):
        """
        Returns the sequence of a given number
        """
        return self.formula(n)

    @property
    def __to_dict__(self):
        """
        :return: dictionary from 0 to to_num var
        """

        def mapper(x):
            if x > 1:
                return x, self.__seq__(x)
            else:
                return x, [0]

        return dict(map(mapper, self.r))

    @property
    def __seq_last__(self):
        """
        :return: gives the last number of each seq
        """

        def mapper(x):
            if x > 1:
                return self.__seq__(x)[-1]
            else:
                return 0

        return list(map(mapper, self.r))

    @property
    def __seq_len__(self):
        """
        :return: gives the len of each seq
        """

        def mapper(x):
            if x > 1:
                return len(self.__seq__(x))
            else:
                return 0

        return list(map(mapper, self.r))


class _Sequence(_Dictionary):

    def __init__(self, init_n: int, limit: int, *args, **kwargs):
        """
        Class to compute the sequence or partition it if needed

        :param init_n: initial number
        :param limit: rough length of the sequence
        :param args: params of EvenSeq
        :param kwargs: params of EvenSeq
        """

        super(_Sequence, self).__init__(*args, **kwargs)

        self.n = init_n
        self.pos = 0  # get position of repeated sequence
        self.lim = limit

        self.dct = self.__to_dict__
        self.lst = self.__seq_last__
        self.lng = self.__seq_len__

    def __yield__(self):
        """
        yields the sequence of
            length: param limit
            init: param number
        """
        n = self.n
        m = self.lim - 1
        yield [n]

        # while num is not in the dict
        while n > self.max_key:
            if m > 0:
                n = self.formula(n)
                m = m - 1
                yield [n]
            else:
                break
        else:
            # while num doesn't give
            # a repeated sequence
            while n is not self.lst[n]:
                if m > 0:
                    m = m - self.lng[n]
                    n = self.lst[n]
                    yield self.dct[n]
                else:
                    break
            else:
                from math import ceil

                self.pos = self.lim - m
                # repeated sequence
                r = ceil(m / self.lng[n])
                for _ in range(r):
                    yield self.dct[n]


class Sequence(_Sequence):

    def __init__(self, initial_number: int, sequence_limit: int,
                 min_partitions: int = 0):

        assert initial_number > 1, "initial number should be greater than 1"

        super(Sequence, self).__init__(init_n=initial_number, limit=sequence_limit,
                                       to_num=20, min_len=min_partitions)

        self.inter, self.perm = tee(self.__yield__())
        self.temp, self.inter = tee(self.perm)
        self.index = 0
        self.batch = 0
        self._pos_ = self.pos

    def __reset__(func):
        def wrapper(self, *args, **kwargs):
            f = func(self, *args, **kwargs)
            self.temp, self.inter = tee(self.inter)
            self.index = 0
            self.batch = 0
            return f

        return wrapper

    @__reset__
    @property
    def reset(self):
        self.inter, self.perm = self.perm
        return self.inter

    @property
    @__reset__
    def get_sequence(self):
        return self.temp

    @__reset__
    def __get_item__(self, idx):
        if idx < 0:
            idx = self.__len__() + idx

        batch, pos = self.__position__(idx)
        f = filter(lambda b: b[0] is batch, enumerate(self.temp))
        f = filter(lambda x: isinstance(x, list), iter(next(f)))
        f = map(lambda x: x, next(f))

        for _ in range(pos):
            next(f)

        return next(f)

    @__reset__
    def __position__(self, idx):
        repeat = self.__repeat__
        counter = 0

        length = map(len, self.temp)
        batch_len = next(length)

        while idx >= batch_len:
            if counter < repeat:
                counter += 1
                idx = idx - batch_len
                batch_len = next(length)
            else:
                counter += idx // batch_len
                idx = idx % batch_len

        return counter, idx

    @__reset__
    def __getitem__(self, index):
        if isinstance(index, int):
            item = self.__get_item__(index)
        else:
            item = list()
            stop = index.stop if index.stop else self.__len__() - 1
            start = index.start if index.start else 0
            if index.step:
                rng = (start, stop, index.step)
            else:
                rng = (start, stop)

            for i in range(*rng):
                item.append(self.__get_item__(i))

        return item

    @__reset__
    def get_batch(self, num):
        for _ in range(num - 1):
            next(self.temp)
        else:
            return next(self.temp)

    @property
    @__reset__
    def __total_batch__(self):
        """
        total number of lists in the sequence
        if extender is used it approximately computes
        the length of total elements by:
        self.element_length * min_len
        """
        return sum(map(lambda _: 1, self.temp))

    def __calc__(func):
        def wrapper(self, other):
            lst = []
            for batch in self.temp:
                lst.append(map(func(self, other), batch))

            self.inter = map(lambda x: list(x), lst)
            return self

        return wrapper

    @__calc__
    def __add__(self, other):
        return lambda x: x + other

    @__calc__
    def __sub__(self, other):
        return lambda x: x - other

    @__calc__
    def __mul__(self, other):
        return lambda x: x * other

    @__calc__
    def __pow__(self, power, modulo=None):
        return lambda x: x ** power

    @__calc__
    def __truediv__(self, other):
        return lambda x: x / other

    @__reset__
    def __contains__(self, item):
        for batch in self.temp:
            if item in batch:
                return True
        else:
            return False

    @__reset__
    def __len__(self):
        return sum(map(len, self.temp))

    def __next__(self):
        if self.batch:
            self.index += 1
            return self.batch.pop(0)
        else:
            self.batch = next(self.temp)
            return self.__next__()

    @property
    @__reset__
    def __repeat__(self):
        if not self._pos_:
            k = map(lambda x: self.pos, self.temp)
            self._pos_ = next(filter(lambda a: a, k))

        return self._pos_


if __name__ == '__main__':
    my_sequence = Sequence(2, 10 ** 5, 10 ** 3)
    print(len(my_sequence))  # 100201

    print(my_sequence[1:10])  # [4, 8, 16, 14, 10, 2, 4, 8, 16]
    my_sequence + 10
    print(my_sequence[1:10])  # [14, 18, 26, 24, 20, 12, 14, 18, 26]
    my_sequence * 2
    print(my_sequence[1:10])  # [28, 36, 52, 48, 40, 24, 28, 36, 52]
