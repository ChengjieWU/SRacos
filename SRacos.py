import random
import copy


class SRacos:

    def __init__(self):
        pass

    def opt(self, objective, dimension, budget, k, r, prob):
        data = list()
        for i in range(r):
            x = self.uniform_sample(dimension, None)
            y = objective.eval(x)
            data.append((x, y))
        positive_data, negative_data, best_solution = self.selection(data, k)
        for t in range(budget - r):
            if random.random() < prob:
                x = self.sample_from_racos(dimension, positive_data, negative_data)
            else:
                x = self.uniform_sample(dimension, None)
            y = objective.eval(x)
            inferior = self.replace_wr((x, y), positive_data, 'pos')
            _ = self.replace_wr(inferior, negative_data, 'neg')
            best_solution = positive_data[0]
        return best_solution

    def sample_from_racos(self, dimension, positive_data, negative_data):
        sample_region = copy.deepcopy(dimension)
        x_positive = positive_data[random.randint(0, len(positive_data) - 1)]
        len_negative = len(negative_data)
        index_set = list(range(len(dimension)))
        types = list(map(lambda x: x[2], dimension))
        order = list(map(lambda x: x[3], dimension))
        while len_negative > 0:
            k = index_set[random.randint(0, len(index_set) - 1)]
            x_pos_k = x_positive[0][k]
            # continuous
            if types[k] is True:
                x_negative = negative_data[random.randint(0, len_negative - 1)]
                x_neg_k = x_negative[0][k]
                if x_pos_k < x_neg_k:
                    r = random.uniform(x_pos_k, x_neg_k)
                    if r < sample_region[k][1]:
                        sample_region[k][1] = r
                        i = 0
                        while i < len_negative:
                            if negative_data[i][0][k] >= r:
                                len_negative -= 1
                                itemp = negative_data[i]
                                negative_data[i] = negative_data[len_negative]
                                negative_data[len_negative] = itemp
                            else:
                                i += 1
                else:
                    r = random.uniform(x_neg_k, x_pos_k)
                    if r > sample_region[k][0]:
                        sample_region[k][0] = r
                        i = 0
                        while i < len_negative:
                            if negative_data[i][0][k] <= r:
                                len_negative -= 1
                                itemp = negative_data[i]
                                negative_data[i] = negative_data[len_negative]
                                negative_data[len_negative] = itemp
                            else:
                                i += 1
            # discrete
            else:
                if order[k] is True:
                    x_negative = negative_data[random.randint(0, len_negative - 1)]
                    x_neg_k = x_negative[0][k]
                    if x_pos_k < x_neg_k:
                        # different from continuous version
                        r = random.randint(x_pos_k, x_neg_k - 1)
                        if r < sample_region[k][1]:
                            sample_region[k][1] = r
                            i = 0
                            while i < len_negative:
                                if negative_data[i][0][k] >= r:
                                    len_negative -= 1
                                    itemp = negative_data[i]
                                    negative_data[i] = negative_data[len_negative]
                                    negative_data[len_negative] = itemp
                                else:
                                    i += 1
                    else:
                        r = random.randint(x_neg_k, x_pos_k)
                        if r > sample_region[k][0]:
                            sample_region[k][0] = r
                            i = 0
                            while i < len_negative:
                                if negative_data[i][0][k] <= r:
                                    len_negative -= 1
                                    itemp = negative_data[i]
                                    negative_data[i] = negative_data[len_negative]
                                    negative_data[len_negative] = itemp
                                else:
                                    i += 1
                else:
                    delete = 0
                    i = 0
                    while i < len_negative:
                        if negative_data[i][0][k] != x_pos_k:
                            len_negative -= 1
                            delete += 1
                            itemp = negative_data[i]
                            negative_data[i] = negative_data[len_negative]
                            negative_data[len_negative] = itemp
                        else:
                            i += 1
                    if delete != 0:
                        index_set.remove(k)
        return self.uniform_sample(sample_region, x_positive)

    @staticmethod
    def uniform_sample(dimension, x_pos):
        x = list()
        for i in range(len(dimension)):
            if dimension[i][2] is True:
                value = random.uniform(dimension[i][0], dimension[i][1])
            elif dimension[i][3] is True:
                value = random.randint(dimension[i][0], dimension[i][1])
            else:
                if x_pos is None:
                    rand_index = random.randint(0, len(dimension[i][4]) - 1)
                    value = dimension[i][4][rand_index]
                else:
                    value = x_pos[i]
            x.append(value)
        return x

    @staticmethod
    def selection(data, k):
        new_data = sorted(data, key=lambda item: item[1])
        positive_data = new_data[0: k]
        negative_data = new_data[k: len(new_data)]
        return positive_data, negative_data, positive_data[0]

    def replace_wr(self, item, data, iset_type):
        if iset_type == 'pos':
            index = self.binary_search(data, item, 0, len(data) - 1)
            data.insert(index, item)
            worst_ele = data.pop()
            return worst_ele
        elif iset_type == 'neg':
            worst_index = 0
            for i in range(len(data)):
                if data[i][1] > data[worst_index][1]:
                    worst_index = i
            worst_ele = data[worst_index]
            if worst_ele[1] > item[1]:
                data[worst_index] = item
            else:
                worst_ele = item
            return worst_ele
        else:
            print('error! wait for handling')

    def binary_search(self, iset, x, begin, end):
        """
        Find the first element larger than x.

        :param iset: a solution set
        :param x: a Solution object
        :param begin: begin position
        :param end: end position
        :return: the index of the first element larger than x
        """
        x_value = x[1]
        if x_value <= iset[begin][1]:
            return begin
        if x_value >= iset[end][1]:
            return end + 1
        if end == begin + 1:
            return end
        mid = (begin + end) // 2
        if x_value <= iset[mid][1]:
            return self.binary_search(iset, x, begin, mid)
        else:
            return self.binary_search(iset, x, mid, end)

