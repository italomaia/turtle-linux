# -*- coding: iso-8859-1 -*-
claves = """
nombre
audiencia
objeto
hechizo
historyintro
historygood
historybad
titulo
params
""".strip().split("\n")

#
# Explicación dificultad de los niveles
# 
# La idea es que en algunos casos sea dificil porque el hechizo es largo, y en otros casos
# tiene que ser dificil porque el tiempo es poco.
# 
# En los primeros niveles, tiene que ser facil segun ambos parametros, y en los ultimos 
# dificiles tambien los dos.
# 
# Anote entonces los largos de cada hechizo (que estan buenisimos, no los cambiemos) y le
# asigne un tiempo total en funcion de el tipo de dificultad y el nro de nivel. A partir de
# eso calculo el tiempo por letra.
#
#   Nombre nivel     caracs  tiempo  secs/char  Descripcion
#   ---------------  ------  ------  ---------  -----------
#   Teatro prestado     45      35      0.77    Es el mas facil, la intro
#   Opera               57      27      0.47    Mas dificil, pero no tanto
#   Magic arena        102      50      0.49    Muy largo, tiempo que le alcance
#   Fiesta musical     117      48      0.41    Mas largo, menos tiempo
#   Las Vegas          134      48      0.36    Mas largo, tiempo apretado
#   Black magic        119      40      0.34    Menos letras, pero cae mas el tiempo
#   Tatooine           114      35      0.31    Sigue acortandose, menos tiempo
#   Area 51            113      30      0.27    Igual de largo, bastante menos tiempo
#   Graveyard          134      25      0.19    Mas largo, el tiempo es aun menor
#   El lugar feliz     145      20      0.14    Mas complicado que la mierda
#

from people import Wardrobe, all_wardrobes

fullydressed = {
    "behind":0.5,
    "body":1,
    "hair":0.9,
    "underware":0.95,
    "tops":1,
    "bottoms":1,
    "shoes":1,
    "jackets":1,
    "hats":0.01,
    "infront":0.85,
}

gothdressed = {
    "behind":0.5,
    "body":1,
    "hair":0.95,
    "underware":0.95,
    "tops":0.5,
    "bottoms":0.5,
    "shoes":0.7,
    "jackets":0.3,
    "hats":0.3,
    "infront":0.40,
}

enmascarados = {
    "behind":0.5,
    "body":1,
    "hair":0.9,
    "underware":0.95,
    "tops":1,
    "bottoms":1,
    "shoes":1,
    "jackets":1,
    "hats":0.70,
    "infront":0.85,
}

enpelotas = {
    "behind":0.5,
    "body":1,
    "hair":0.99,
    "underware":0.65,
    "tops":0,
    "bottoms":0,
    "shoes":0,
    "jackets":0,
    "hats":0.01,
    "infront":0.12,
}


textosNiveles = [
    (
        "Lousy Pub",
        [Wardrobe('audiencia/girl/', 'articles0.txt'), 
         Wardrobe('audiencia/boy/', 'articles0.txt')],
        "conejo2",     # conejo
        "hocus pocus, disappear now, desaparecelo chico.",
"""Cast the spell 
as fast and accurately as you can. 

You can backspace and fix 
your mistakes.""",

"""Great! 

You receive an offer to perform 
in the "Paris Opera".""",
"""You are not even worthy of 
this demo level.""",
        "Orko",
        dict(tiempo_por_caracter=0.77, preferencia_precision=0.5)
    ),

    (
        "Paris Opera",
        #"Gente vestida bien",
        [Wardrobe('audiencia/fashion_girl/', 'articles1.txt', fullydressed),
         Wardrobe('audiencia/boy/', 'articles1.txt', fullydressed)],
        "mask",  # La mascara del fantasma de la opera
        "evanesco simulatio, phantasma spectaculum. initium capere.",
"""Disappear the Phantom's mask, 

that will embarass him and 
make him leave.""",
"""Your act was great! 

You are invited to perform the 
Halftime show at the local
basquetball finals.""",
"""You blew it, 
your father disinherited you. 

You get a job coding ruby on rails.""",
        "Lord Zedd",
        dict(tiempo_por_caracter=0.47, preferencia_precision=0.5)
    ),


    (
        "Magic arena",
        all_wardrobes, #""Jugadores de basquet o deportistas",
        "zapatillas", # Zapatillas grandes
        "luckyus calceus sneakerus, evanesco consagrus, valius playerus, propugnator turma championus.",
"""The locals are loosing by 12,
you must disappear the
visitor's MVP lucky sneakers.""",

"""Thanks to your help the locals win
and you get invited to do your trick
at the after party.""",
"""An Angry mob of the local fans
chases you around the stadium.""",
        "David Copperfield",
        dict(tiempo_por_caracter=0.49, preferencia_precision=0.5)
    ),


    (
        "Goth party",
        #""Hip-hoperos o darkies",
        [Wardrobe('audiencia/goth/', 'articles3.txt', gothdressed), ],
        "vicios", # Alcohol, drogas, hacer un mix
        "sexus drugus rockanrolus, captivus crowdimus yowasaaap. cops and hardcopy marihuanus boozelion, cocuchus chuchu fuchu.",
"""You were supposed to disappear 
a milli vanilli cd, 
instead you must vanish the 
drugs to hide them 
from the cops.""",
"""You got away clean, 
and kept a lot of famous people
out of jail. 

You are going to Las Vegas now!!""",
"""You go to jail charged with 
drug possession. 
And become RAUL's new girlfriend.""",
        "Skeletor",
        dict(tiempo_por_caracter=0.41, preferencia_precision=0.5)
    ),


    (
        "Las Vegas",
        all_wardrobes, #""Gente adinerada",
        "docs", # papeles y documentos
        "factus taxus nulus, nilun actin, evaDus fiscus IRSus, whySaw Elvis Bellagium 11 ocean's cardus impustum disapiros ipsofactum.",
"""You get to Las Vegas 
to perform in a Casino, but 
the owners want to take 
advantage of your power 
to evade taxes.""",
"""The IRS wants you for beeing 
an accesory to tax evasion. 

They send you Africa where
they'll never find you""",
"""Your act was a total failure, 
you got wasted and lost 
all your money playing craps.""",
        "Mumm-Ra",
        dict(tiempo_por_caracter=0.36, preferencia_precision=0.5)
    ),


    (
        "Black magic",
        #""Africanitos de la tribu",
        [Wardrobe('audiencia/girl/', 'articles5.txt', fullydressed),
         Wardrobe('audiencia/boy/', 'articles5.txt', fullydressed)],
        "mucielago", # Un muricélago, o algún animal raro
        "Batsimus chicaka aFrIcuN triBuson, ill chikakun medicor, nigrum. comedo. crudus...pain cooking Shutlewor meellon cHuNgo.",
"""You go to live with a tribe 
in africa, they find out
you are a wizard and want 
you to heal their ill 
sacred animal""",
"""You disappeared the sacred animal. 
The angry natives start chasing 
you around the jungle.""",
"""The natives made a tasty
casserole out of you.""",
        "Harry Potter",
        dict(tiempo_por_caracter=0.34, preferencia_precision=0.5)
    ),

    (
        "Tatooine",
        [Wardrobe('audiencia/boy/', 'articles6.txt', enmascarados)],
        "aspiradora", # Aspiradora loca
        "Arturitum Vacuumcleanerum Ev4niscum c3p0 venusiun rescusum grossum ph1ll1ps, disapirum spacious robotitus shakulus.",
"""While running away from the natives, 
a spaceship abducts 
you. The venusians ask you to help 
them vanish a hitchhiker.""",
"""Since you were so helpfull, 
the venusians send you back to earth 
in an individual spaceship.""",
"""Because you were unwilling to cooperate, 
the venusians performed a 
'light saber anal probing' on you.""",
        "Mandrake",
        dict(tiempo_por_caracter=0.31, preferencia_precision=0.5)
    ),

    (
        "Area 51",
        [Wardrobe('audiencia/boy/', 'articles_alien.txt', {
    "behind":0.5,
    "body":1,
    "hair":0.6,
    "underware":0.30,
    "tops":0.3,
    "bottoms":0.3,
    "shoes":0.3,
    "jackets":0.05,
    "hats":0.01,
    "infront":0.85,
}), Wardrobe('audiencia/boy/', 'articles_mib.txt', {
    "behind":0.5,
    "body":1,
    "hair":0.90,
    "underware":0.30,
    "tops":1,
    "bottoms":1,
    "shoes":1,
    "jackets":1,
    "hats":0.01,
    "infront":1,
})],"alien", # un marcianito de roswell
        "Marcianus 51area alf rosswellin didosong untilyourestingherewithme evanisum marcianus y guarda que viene molderrr.",
"""Your ship was running a pirated 
OS and crashed in new mexico. 
The FBI captures you and asks you 
to disappear some evidence of 
the alien landings.""",
"""Now that the evidence exists 
only on your memory,
the FBI makes sure you won't talk 
by putting a cap in your head""",
"""You couldn't do it. 
But you'll have a lot of time 
to practice since you are
never leaving area 51""",
        "Harry Houdini",
        dict(tiempo_por_caracter=0.27, preferencia_precision=0.5)
    ),

    (
        "Graveyard",
       [Wardrobe('audiencia/boy/', 'articles8.txt', {
    "behind":0.5,
    "body":1,
    "hair":0.6,
    "underware":0.30,
    "tops":0.3,
    "bottoms":0.3,
    "shoes":0.3,
    "jackets":0.05,
    "hats":0.01,
    "infront":0.85,
})], #""Esqueletos",
        "anubis", # Estatuilla de Anubis
        "vaderetrum satinus anubisun chungus, transformix this decayed form to Mumm-ra the Everliving and the puwur of christus will savius vox.",
"""Ok, you died, and went to hell, 
you can escape to heaven by 
disappearing Anubis. 

All the dead gather around to watch...""",
"""You did it!!! 
Now you go to heaven, that happy
place we all dream about as kids,
that place where men and women
love each other.""",
"""You stay in hell. At least 
you won't have problems 
finding a lawyer if you ever 
come to need one.""",
        "Merlyn",
        dict(tiempo_por_caracter=0.19, preferencia_precision=0.5)
    ),


    (
        "Hugh's Place",
        #""Todos desnudos",
        [Wardrobe('audiencia/fashion_girl/', 'articles9.txt', enpelotas), 
         Wardrobe('audiencia/boy/', 'articles9.txt', enpelotas)],
        "cabra", # CUZCO la cabra
        "caelum CUZCUS 13 paradisiun, revivisco animalis playboyus housus, pornus sexus gross klunx workus my clunk essta noshi inbolus minusem. miau miau.",
"""Here we are, it's beautiful, 
everything that disappears here goes 
back to earth, so you are going to 
revive a lovely goat now!""",
"""Congratulations! 

You fullfilled your destiny 
as a Magician!""",
"""Mmm... 

Too bad you couldn't do it, but hey, 
a horde of naked angels offers 
to console you!!""",
        "Gandalf",
        dict(tiempo_por_caracter=0.14, preferencia_precision=0.5)
    ),
]#[1:]

class Niveles:
    def __init__(self, keys, values):
        for k,v in zip(keys, values):
            setattr(self, k, v)

niveles = [ Niveles(claves, values) for values in textosNiveles ]

if __name__ == "__main__":
    for n in niveles:
        print dir(n)
