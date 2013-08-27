# -*- coding: utf-8 -*-

from Captcha.Visual import Text, Backgrounds, Distortions, ImageCaptcha
from Captcha import Words
import random

class ChineseIdiomCaptcha(ImageCaptcha):
    """A fixed-solution CAPTCHA that can be used to hide email addresses or URLs from bots"""
    fontFactory = Text.FontFactory(16, "cn/simyou.ttf")
    defaultSize = (80, 25)
    
    def __init__(self, solution=u'验证码', from_list=True):
        if from_list:
            idiom_chinese = Words.WordList("basic-english", minLength=5, maxLength=8)
            self.solution = idiom_chinese.pick()
        else:
            self.solution = solution

        super(ChineseIdiomCaptcha, self).__init__()

    def getLayers(self):
        self.addSolution(self.solution)

        textLayer = Text.TextLayer(self.solution,
                                   borderSize = 2,
                                   fontFactory = self.fontFactory)

        return [
            Backgrounds.CroppedImage(),
            textLayer,
            Distortions.SineWarp(amplitudeRange = (1, 1)),
            ]

class EnglishWordCaptcha(ImageCaptcha):
    """A fixed-solution CAPTCHA that can be used to hide email addresses or URLs from bots"""
    fontFactory = Text.FontFactory(16, "vera/Vera.ttf")
    defaultSize = (80, 25)
    
    def __init__(self, solution=u'验证码', from_list=True):
        if from_list:
            self.solution = Words.basic_english_restricted.pick()
        else:
            self.solution = solution

        super(EnglishWordCaptcha, self).__init__()

    def getLayers(self):
        self.addSolution(self.solution)

        textLayer = Text.TextLayer(self.solution,
                                   borderSize = 1,
                                   fontFactory = self.fontFactory)

        return [random.choice([
                               Backgrounds.TiledImage()
                               ]),
                textLayer,
                Distortions.SineWarp(),
            ]

class NumberCaptcha(ImageCaptcha):
    """A fixed-solution CAPTCHA that can be used to hide email addresses or URLs from bots"""
    fontFactory = Text.FontFactory(16, "vera/Vera.ttf")
    defaultSize = (60, 24)
    
    def __init__(self, digits=4):
        if digits > 10:
            digits = 10
        self.solution = ''.join([ '%s'%i for i in random.sample(range(0, 10), digits)])

        super(NumberCaptcha, self).__init__()

    def getLayers(self):
        self.addSolution(self.solution)

        textLayer = Text.TextLayer(self.solution,
                                   borderSize = 1,
                                   fontFactory = self.fontFactory)

        return [# random.choice([ Backgrounds.TiledImage() ]),
                [Backgrounds.SolidColor('white'), Backgrounds.RandomDots(colors=['yellow', 'blue', 'green', 'red'], numDots=10)],
                textLayer,
                Distortions.SineWarp(),
            ]

if __name__ == '__main__':
    g = ChineseIdiomCaptcha()
    i = g.render()
    i.save("output.png")