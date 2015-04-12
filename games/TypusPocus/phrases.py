# -*- coding: utf-8 -*-
#
# A simple phrase generator using a modifiable grammar

import random
import string
from string import Template

grammar = {

# "pacta tertis nec nocent nec prosunt",

'zen_of_python' : [ "Beautiful is better than ugly","Explicit is better than implicit","Simple is better than complex","Complex is better than complicated","Flat is better than nested","Sparse is better than dense","Readability counts","Special cases aren't special enough to break the rules","Although practicality beats purity","Errors should never pass silently","Unless explicitly silenced","In the face of ambiguity, refuse the temptation to guess","There should be one-- and preferably only one --obvious way to do it","Although that way may not be obvious at first unless you're Dutch","Now is better than never","Although never is often better than *right* now","If the implementation is hard to explain, it's a bad idea","If the implementation is easy to explain, it may be a good idea","Namespaces are one honking great idea -- let's do more of those!"],

'preposition' : ["aboard","about","above","absent","across","after","against","along","alongside","amid","amidst","among","amongst","around","as","at","atop","before","behind","below","beneath","beside","besides","between","beyond","by","despite","down","during","except","following","for","from","in","inside","into","like","near","nearest","notwithstanding","of","off","on","onto","opposite","out","outside","over","past","round","since","through","throughout","till","to","toward","towards","under","underneath","unlike","until","up","upon","with","within","without"],

'verb' : ["expeleriamus", "habemus", "levitatio", "cogitum", "possum", "factito", "agito" ],

'digit' : ["one","two","three","four","five","six","seven","eight","nine"],
'number10_19' : ["ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","eighteen","nineteen",],
'ten' : ["twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"],
'number' : ["$digit","$number10_19","$ten"],

'sexual_thing' : ["boobs", "boobies", "teats", "nipples", "tits", "butts"],

'excellent' : ['excellent','nice','awesome','wonderful','incredible',"inspiring","amazing","superb"],

'animal_part' : ['head','eye','tail','leg','arm','elbow','tongue','brain','lung','nose','knee','toe','foot','shoulder','ankle','neck','jaw','teeth','stomach','testicle','spleen','heart','liver',],

'adjective': [ "$excellent", "insolent", "bizarre", "horribilis","perfectis","bad","jittery","purple","tan","better","jolly","quaint","tender","beautiful","kind","quiet","testy","big","long","quick","tricky","black","lazy","quickest","tough","blue","bright","magnificent","magenta","rainy","rare","ugly","ugliest","clumsy","many","ratty","vast","crazy","mighty","red","watery","dizzy","mushy","roasted","wasteful","dull","nasty","robust","stinky","fat","new","round","wonderful","frail","nice","sad","yellow","friendly","nosy","scary","yummy","funny","nutty","scrawny","zany","great","nutritious","short","green","odd","silly","gigantic","orange","stingy","gorgeous","ordinary","strange","grumpy","pretty","striped","handsome","precious","spotty","happy","prickly","tart","horrible","tall","itchy","tame"],

'animal': ["alligator","alpaca","ant","ape","armadillo","ass","baboon","badger","bat","bear","bee","beetle","bird","bison","bittern","boar","buffalo","butterfly","buzzard","camel","cat","cattle","cheetah","chicken","chimpanzee","cockroach","cod","coot","coyote","crane","crocodile","deer","dog","dolphin","donkey","dove","duck","eagle","eel","elephant","elk","falcon","ferret","finch","flamingo","fly","fox","frog","gerbil","giraffe","gnat","gnu","goat","goldfinch","goose","gorilla","greyhound","grouse","guinea pig","gull","hamster","hare","hawk","hedgehog","heron","hippopotamus","hog","horse","hummingbird","hyena","impala","kangaroo","koala","lark","lemur","leopard","lion","llama","lobster","locust","magpie","mallard","manatee","mink","mole","monkey","moose","mosquito","mouse","mule","nighthawk","nightingale","opossum","ostrich","otter","ox","panda","parrot","partridge","pelican","penguin","pig","pheasant","pigeon","polar bear","polecat","porcupine","porpoise","possum","prairie dog","python","quail","rabbit","raccoon","rat","raven","reindeer","rhinoceros","rook","salmon","seal","sea lion","shark","sheep","skunk","snake","snipe","sparrow","spider","squirrel","starling","stork","swallow","swan","termite","tiger","toad","trout","turkey","turtle","viper","wallaby","walrus","wasp","weasel","whale","widgeon","wolf","wombat","woodchuck","woodcock","woodpecker","wren","yak","zebra"],

'latin_noun' : ["amicitia", "potentia", "scientia", "aequalitas", "dignitas", "facilitas", "gravitas", "libertas", "novitas", "potestas", "qualitas", "veritas", "certitudo", "longitudo", "magnitudo", "multitudo", "similitudo","libiditus",],

'noun': ["$animal", "$latin_noun", "$animal_part"],

'author' : ['tenuki','alecu','lucio','leito','facundo','riq','nubis','pabloz','chaghi'],
'women_name' : ['Olivia','Charlotte','Emily','Chloe','Ella','Jessica','Isabella','Sophie','Mia','Emma'],
'men_name' : ['Jack','James','Lachlan','Benjamin','Joshua','Ryan','John','Patrick','Samuel','William'],
'name' : ['$author', '$men_name','$women_name'],


'pronoun' : ['I','you','yo','she','he','we','they'],

'subject' : ['$animal'],

'phrase1' : ["python","god","deus","pamela",],

'phrase2' : ["holy python", "odius perl", "greatest guido", "import this","pythonus idolotrus", "modus operandi","ipso facto","$number $animal"],

'phrase3' : ["bizarre fragances expeleriamus","horribilis fungus habemus",'super califragilistic expialedocious',"super $sexual_thing enlargio","intensum odoris expeleriamus","enormis $animal_part habeant","hideous hair electrifiamus","super top model convertimus","incredibilis muscles damus","more money creamus","in love transformis","totalis mind erasing","pacta sunt servanda","bona fides damus","alicuius amore ardere","veni vidi vici","libido incrementus forever"],

'phrase4' : ["$verb $preposition $adjective $noun", "your $sexual_thing are $excellent", "$number $animal $preposition $noun","$author $verb $excellent $animal_part"],

'phrase5' : ["$subject $verb $preposition $adjective $noun",],

'phrase6' : ["$number $animal_part $verb $preposition $adjective $noun",],

'phrase7' : ["$number $adjective $subject $verb $preposition $adjective $noun"],

'phrase8' : ["$number $subject $animal_part $verb $preposition $adjective $adjective $noun"],

'spell_begin' : ["hocus pocus", "abracadabra",],

'now' : ["right now","now","", "at this moment", "immediately", "without delay", "instantly", "at once", "right away", ],

'pliz' : ["","please"],

'disappear' : ["disappear", "go away", "evaporate", "vanish", "dematerialise", "dematerialize", "bob under", ],

'spell_end' : ["$pliz $disappear $now"],

'funny_phrase' : ["bizarre fragances expeleriamus","horribilis fungus habemus","pythonus idolotrus"],
}

MAXPHRASE = 8

class Phrase:
    def __init__(self):
        self.__phrase = ''
        self.setGrammar( random.choice( grammar["phrase8"] ) )

    def replace(self, aString ):
        """parses a string, and replaces all the variables with another string,
        which might contain new variables, but will be replaced as well."""

        ret = []
        words = string.split(aString)
        for word in words:
            # variables start with $
            if word[0] == '$':
            # little optimization
                try:
                    # make it fail
                    Template( word ).substitute()
                except KeyError, key:
                    keystr = str(key)[1:-1]
                    varstr = random.choice( grammar[ keystr ] )
                    ret.extend( self.replace( Template( word ).substitute( { keystr :  varstr} ) ) )
            else:
                ret.append( word )
        return ret

    def setGrammar( self, phrase ):
        """sets a grammar to be replaced"""
        self.__phrase = phrase

    def getGrammar( self ):
        """returns the grammar."""
        return self.__phrase
         

    def getPhrase(self):
        """ returns the generated and replaced phrase """
        ret = self.replace( self.__phrase ) 
        return string.join(ret)


class PhraseLen( Phrase ):
    """returns a phrase of a fixed len of words."""
    def __init__( self, l ):
        Phrase.__init__(self)
        self.__len = l
        self.findPhrase()

    def findPhrase( self ):
        i = self.__len

        comma = ""
        phrase = ""
        while i > 0:
            # hardcoded, if you want to support more, just add to grammar
            if i > MAXPHRASE:
                d = random.randint(1, MAXPHRASE)
            else:
                d = i

            name = "$phrase%d" % d
            phrase += comma + name
            comma = ", "
            i -= d

        self.setGrammar( phrase )

class Spell( PhraseLen ):
    """Construct a valid spell, with beginning and ending words."""
    def __init__( self, l, objectToVanish = None ):

        begin = self.replace( random.choice( grammar['spell_begin'] ) )
        end = self.replace( random.choice( grammar['spell_end'] ) )
        PhraseLen.__init__(self,l-( len(begin) + len(end) ) )

        g =  self.getGrammar()
        if g:
            g += ', '
        self.setGrammar( string.join(begin)
                           + ', '
                           + g
                           + string.join(end) )

    def getPhrase(self):
        p = PhraseLen.getPhrase(self)
        return string.strip(p) + '.'

class FunnyPhrase( Phrase ):
    """returns a phrase that should be funny."""
    def init( self ):
        self.Phrase.__init__(self)
        self.setGrammar( random.choice( grammar["funny_phrase"] ) )

if __name__ == "__main__":
    for i in range(1,7):
        print '---------------------'
#        print Phrase().getPhrase()
        p = Spell(i).getPhrase() 
        print "Len(%d,%d): %s" % (i, len(p), p)
