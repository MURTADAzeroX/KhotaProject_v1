from copy import deepcopy


def check_game(data):
    GCV1 = [[0, 1, 2], [0, 3, 6],
            [3, 4, 5], [1, 4, 7],
            [6, 7, 8], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
            ]

    for i in GCV1:
        score = sum([data[i[0]], data[i[1]], data[i[2]]])
        if score == 3:
            print('X Wins')
            return True
        elif score == -3:
            print('O Wins')
            return True

    return False


def ConvertToPath(game):
    Path = []
    for i in game:
        if i == 'X':
            Path.append(1)
        elif i == 'O':
            Path.append(-1)
        else:
            Path.append(0)
    return Path


class AIEngine:
    def __init__(self):
        self.SearchDepth = 6
        self.GameChecker3x3 = {0: [0, 3, 6], 1: [0, 4], 2: [0, 5, 7],
                               3: [1, 3], 4: [1, 4, 6, 7], 5: [1, 5],
                               6: [2, 3, 7], 7: [2, 4], 8: [2, 5, 6]}
        self.StartingDepth = None
        self.repeated_ele = {}

    def GetScore3x3(self, path):
        Data = [0] * 8
        for i, ele in enumerate(path):
            if ele == 1:
                for k in self.GameChecker3x3[i]:
                    Data[k] += 1
            elif ele == -1:
                for k in self.GameChecker3x3[i]:
                    Data[k] -= 1

        return Data

    def Best(self, path):
        LoopKey = [i for i, ele in enumerate(path) if ele == 0]
        StartingData = self.GetScore3x3(path)
        switch = (-1) ** ((path.count(0) + 1) % 2)
        depth = path.count(0)
        self.StartingDepth = depth
        if self.SearchDepth > self.StartingDepth:
            self.SearchDepth = self.StartingDepth

        result = self.BuildTree(switch, depth, StartingData, LoopKey, path)
        print(result)
        if switch == 1:
            return LoopKey[result.index(max(result))]
        else:
            return LoopKey[result.index(min(result))]

    def BuildTree(self, switch, depth, WinCheck, LoopKeys, path):
        DATA = []
        if depth <= self.StartingDepth - self.SearchDepth:
            return 0
        for i in LoopKeys:
            NewPath = deepcopy(path)
            NewPath[i] = switch

            if self.repeated_ele.get(str(NewPath)) is not None:
                ComingData = self.repeated_ele[str(NewPath)]
            else:
                NewWinCheck = deepcopy(WinCheck)
                if switch == 1:
                    for s in self.GameChecker3x3[i]:
                        NewWinCheck[s] += 1
                        if NewWinCheck[s] == 3:
                            if depth == self.StartingDepth:
                                return [i * (k == i) for k in LoopKeys]
                            else:
                                return 10 ** depth + (5 * NewWinCheck.count(2)) ** depth - \
                                       (5 * NewWinCheck.count(-2)) ** depth / 100
                else:
                    for s in self.GameChecker3x3[i]:
                        NewWinCheck[s] -= 1
                        if NewWinCheck[s] == -3:
                            if depth == self.StartingDepth:
                                return [-i * (k == i) for k in LoopKeys]
                            else:
                                return -1 * (10 ** depth + (5 * NewWinCheck.count(-2)) ** depth -
                                             (5 * NewWinCheck.count(2)) ** depth / 100)

                NewLoopKeys = deepcopy(LoopKeys)
                NewLoopKeys.remove(i)

                ComingData = self.BuildTree(switch * -1, depth - 1, NewWinCheck, NewLoopKeys, NewPath)

                self.repeated_ele[str(NewPath)] = ComingData

            DATA += [ComingData]

        if depth == self.StartingDepth:
            return DATA
        elif switch == 1:
            return max(DATA)
        else:
            return min(DATA)


if __name__ == '__main__':
    engine = AIEngine()
    # 1 == X, -1 == O,  0 == nothing
    StartStat = [1, 0, 0,
                 0, 0, 0,
                 0, 0, 0]
    # take game as list
    BestMove = engine.Best(StartStat)
    # then it gives the best index to play in the game
    print(BestMove)
