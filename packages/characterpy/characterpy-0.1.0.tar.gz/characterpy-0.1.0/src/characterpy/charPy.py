import csv
#import numpy as np

classes = {
    'Artificer':[8,'int',['int'],'half'],
    'Barbarian':[12,'str',['str','con'],'non'],
    'Bard':[8,'cha',['cha','dex'],'full'],
    'Cleric':[8,'wis',['wis'],'full'],
    'Druid':[8,'wis',['wis'],'full'],
    'Fighter':[10,'int',['str','con'],'non'],
    'Monk':[8,'wis'],
    'Paladin':[10,'cha'],
    'Ranger':[10,'wis'],
    'Rogue':[8,'int'],
    'Sorcerer':[6,'cha'],
    'Warlock':[8,'cha',['cha'],'non'],
    'Wizard':[6,'int',['int'],'full']
    }

def readCsv(filepath,rowHeaders = False,colNames = False):
        rows = []
        try:
            with open(f'{filepath}', mode ='r')as file:
                csvFile = csv.reader(file)
                for line in csvFile:
                    try:
                        b = line.index('')
                        a = line[0:b]
                    except:
                        a = line[0:]
                        #print(a)
                        #print(a[0])
                        if len(a) == 1:
                            a = a[0]
                            #Convert to int if possible!
                            try:
                                a = int(a)
                                #print('Integered')
                            except:
                                #print('CANT INT IT')
                                a = a
                                if a == '[]':
                                    a = []
                            #print(line[0],a)
                    rows.append(a)
            return rows
        except:
            return -1

def pStr(val):
    if val > 0:
        val = "+"+str(val)
        return val
    if val == 0:
        return ' 0'
    else:
        return val

def it(head,val='',val2='',totsp = 22, buffer = True, lftbuf = False):
    totsp = totsp-1
    ret = ""
    val = str(val)
    head = str(head)
    if val2 != '':
        val2 = str(val2)
        val = val + ' ' + val2
    vallen = len(val)
    headlen = len(head)
    if buffer == True:
        ret = ' ' + head + (' ' * (totsp-headlen-vallen-1)) + val + ' '
    else:
        ret = head + (' ' * (totsp-headlen-vallen+1))+val
    if lftbuf == True:
        ret = "#"+ret
    return ret

class Character:
    #Factories?
    def updateAll(self):
        print('ooga')
        rows = [
            ['name',self.name],
            ['characterClass',self.charclass],
            ['subclass',self.subclass],
            ['background',self.background],
            ['race',self.race],
            ['allignment',self.allignment],
            ['exp',self.exp],
            ['level',self.level],
            ['strength',self.strength],
            ['dexterity',self.dexterity],
            ['constitution',self.constitution],
            ['intelligence',self.intelligence],
            ['wisdom',self.wisdom],
            ['charisma',self.charisma],
            ['expertise',*self.expertise],
            ['proficient',*self.proficient],
            ['joat',self.joat],
            ['currentHP',self.currentHP],
            ['tempHP',self.tempHP],
            ['money',*self.money],
            ['spellSlots',*self.spellSlots],
            ['spells',*self.spells],
            ['xtraSaves',*self.xtraSaves]]
        #print(rows)
        with open(f'./Characters/{self.name}_char.csv', 'w') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile,lineterminator ='\n')
            # writing the data rows
            csvwriter.writerows(rows)            
        print('updated stats')

    def readAll(self):
        print(self)

    def classicConsole(self,space=22):
        print('Hooo')
        cols = []
        rowSep = "="*space
        #SETUP THE FIRST COLUMN
        col1 = [rowSep]
        [col1.append(i) for i in [
            it(self.name),
            it('Level ' + str(self.level)),
            it(self.charclass),
            it(self.subclass),
            rowSep]]
        for i in range(6):
            l = it(self.abilityNames[i],self.abilityScores[i],pStr(self.modifiers[self.abilityTags[i]]))
            col1.append(l)
        [col1.append(i) for i in [
            rowSep,
            it('Passive',self.passivePerception),
            it('Perception'),
            rowSep]]
        for i in range(5):
            l = it(self.moneyNames[i],self.money[i])
            col1.append(l)
        col1.append(rowSep)
        col1.append(it('SPELL SLOTS'))
        for i in range(1,10):
            l = it('Level '+str(i),str(self.spellSlots[i-1]+'/'+str(self.totalSlots[i-1])))
            col1.append(l)
        cols.append(col1)
        
        #SETUP COL 2
        col2 = [rowSep]
        col2.append(it('Proficiency Bonus',pStr(self.proficiencyBonus)))
        col2.append(it('Inspiration'))
        col2.append(it('Initiative',pStr(self.modifiers[self.abilityTags[1]])))
        col2.append(rowSep)
        col2.append(it('SAVING THROWS'))
        for i in range(6):
            s = self.abilityNames[i]
            l = it(s,self.saves[self.abilityTags[i]])
            col2.append(l)

        col2.append(rowSep)
        col2.append(it('SKILLS'))    
        for i in range(len(self.skillsList)):
            s = self.skillsList[i]
            sAdj = s+self.pS(s)
            l = it(sAdj,pStr(self.skills[s]))
            col2.append(l)
        
        cols.append(col2)

        #SETUP COL 3
        print(self.pS(classes[self.charclass][1]))
        col3 = [rowSep]
        [col3.append(i) for i in [
            it('Armor Class'),
            it('Max HP',self.hitpointMax),
            it('Current HP',self.currentHP),
            it('Temp HP',self.tempHP),
            it('Hitdie'),
            rowSep,
            it('DEATH SAVES'),
            it('Success'),
            it('Failure'),
            rowSep,
            it('Spell Save DC',str(self.modifiers[classes[self.charclass][1]] + self.proficiencyBonus + 10)),
            it('Spell Atk Mod')]]
        cols.append(col3)

        
        colLens = [len(i) for i in cols]
        height = max(colLens)
        
        for col in cols:
            colLen = len(col)
            if colLen < height:
                for i in range(height - colLen):
                    col.append(' '*space)

        for i in range(height):
            s = "#"
            for x in cols:
                s = s+str(x[i])+"#"
            print(s)

        s = "#"   
        for x in cols:
            
            s = s+str(x[0])+"#"
        print(s)
        
    def showSpells(self,space=22):
        rowSep = '#'+("="*space)+'#'
        print(rowSep)
        print('Cantrips')
        print(rowSep)
        [print('# ' + spell[0]) for spell in self.spellStats if int(spell[6]) == 0]
        
        for level in range(1,10):
            print(rowSep)
            print('# Level ' + str(level) + ' Spells #')
            [print('# ' + spell[0]) for spell in self.spellStats if int(spell[6]) == int(level)]

    def pS(self,name):
        #GET PROFICIENCY STARS
        saves = ['str','cha','int','wis','dex','con']
        if name in saves:
            if name in self.saveProficiency:
                return '*'
            else:
                return ''
        else:
            if name in self.expertise:
                return '**'
            elif name in self.proficient:
                return '*'
            else:
                return ''
        

    @staticmethod
    def createCharacter(       
        name,
        charclass = 'NA',
        subclass = 'NA',
        background = 'NA',
        race = 'NA',
        allignment = 'NA',
        exp = 0,
        level = 1,
        strength = 0,
        dexterity = 0,
        constitution = 0,
        intelligence = 0,
        wisdom = 0,
        charisma = 0,
        expertise = [],
        proficient = [],
        joat = 0,
        currentHP = 0,
        tempHP = 0,
        money = [0,0,0,0,0],
        spellSlots = [0,0,0,0,0,0,0,0,0],
        spells = [],
        xtraSaves = []):

        print(f'Created new blank character')

        #Save character csv
        open(f'./Characters/{name}_char.csv', 'w', newline='')
        #probably some update character function
        #init with the variables VV
        character = Character(name,
        charclass,
        subclass,
        background,
        race,
        allignment,
        exp,
        level,
        strength,
        dexterity,
        constitution,
        intelligence,
        wisdom,
        charisma,
        expertise,
        proficient,
        joat,
        currentHP,
        tempHP,
        money,
        spellSlots,
        spells,
        xtraSaves)

        
        character.updateAll()
        
        return character

        
    def loadCharacter(name,charDir = './Characters/'):
        print('Loading Character')
        charstats = []
        #try:
        with open(f'{charDir}{name}_char.csv', mode ='r')as file:
            csvFile = csv.reader(file)
            #print(csvFile)
            for line in csvFile:
                #print(line)
                #print(line)
                try:
                    b = line.index('')
                    a = line[1:b]
                except:
                    a = line[1:]
                #print(a)
                #print(a[0])
                if len(a) == 1:
                    a = a[0]
                    #Convert to int if possible!
                    try:
                        a = int(a)
                        #print('Integered')
                    except:
                        #print('CANT INT IT')
                        a = a
                        if a == '[]':
                            a = []
                #print(line[0],a)
                charstats.append(a)
        print(charstats)
        character = Character(*charstats)
        return character
        #except:
            #print('Fatal Error Loading Character')
            #return -1

    
    def __init__(self,
        name,
        charclass,
        subclass,
        background,
        race,
        allignment,
        exp,
        level,
        strength,
        dexterity,
        constitution,
        intelligence,
        wisdom,
        charisma,
        expertise,
        proficient,
        joat,
        currentHP,
        tempHP,
        money,
        spellSlots,
        spells,
        xtraSaves):
        
        #===== Self Input Stats =====
        #Qualitative Traits
        self.name = name
        self.charclass = charclass
        self.subclass = subclass
        self.background = background
        self.race = race
        self.allignment = allignment
        self.exp = exp
        #Level
        self.level = level
        #Ability Scores
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.abilityScores = [strength,dexterity,constitution,intelligence,wisdom,charisma]
        self.abilityNames = ['Strength','Dexterity','Constitution','Intelligence','Wisdom','Charisma']
        self.abilityTags = ['str','dex','con','int','wis','cha']
        #Expertise and Proficiency
        self.expertise = expertise
        self.proficient = proficient
        self.joat = joat
        #Health and HP
        self.currentHP = currentHP
        self.tempHP = tempHP
        
        self.money = money
        self.moneyNames = ["Copper(cp)","Silver(cp)","Electrum(ep)","Gold(gp)","Platinum(pp)"]
            
        #self.inventory = inventory #maybe dictionary
        #self.weaponProficiencies = weaponProficiencies
        #self.otherProficiencies = otherProficiencies
        #self.weapons = weapons #DICT DIC DMG PROF ETC FINNESE
        self.spellSlots = spellSlots
        
        #CREATE SPELLS DICTIONARY FROM GIVEN SPELLS
        self.spellStats = []
        self.spells = spells
        self.xtraSaves = xtraSaves
        print('egg')
        if len(spells) > 0:
            spellList = readCsv('./Stats/Spells.csv')
            spellNames = [i[0] for i in spellList]
            self.spellStats = []
            for spell in spells:
                try:
                    i = spellNames.index(spell)
                    self.spellStats.append(spellList[i])
                    #print(self.spellStats)
                except:
                    print(f'Spell ERROR, "{spell}" not found, could it be spelled wrong?')
        self.spellLevels = {}
        for l in range(0,10):
            print(l)
        print('Spells Loaded')
        print(self.spellStats)
        
        #==== Calculated Values =====
        self.proficiencyBonus = 2 + int((self.level-1)/4)
        #Modifiers dictionary
        self.modifiers = {
            "str":(-5 + int(self.strength/2)),
            "dex":(-5 + int(self.dexterity/2)),
            "con":(-5 + int(self.constitution/2)),
            "int":(-5 + int(self.intelligence/2)),
            "wis":(-5 + int(self.wisdom/2)),
            "cha":(-5 + int(self.charisma/2))
            }
        #Skills dictionary
        self.skills = {
            "Acrobatics":(self.modifiers["dex"]),
            "Animal Handling":(self.modifiers["wis"]),
            "Arcana":(self.modifiers["int"]),
            "Athletics":(self.modifiers["str"]),
            "Deception":(self.modifiers["cha"]),
            "History":(self.modifiers["int"]),
            "Insight":(self.modifiers["wis"]),
            "Intimidation":(self.modifiers["cha"]),
            "Investigation":(self.modifiers["int"]),
            "Medicine":(self.modifiers["wis"]),
            "Nature":(self.modifiers["int"]),
            "Perception":(self.modifiers["wis"]),
            "Performance":(self.modifiers["cha"]),
            "Persuasion":(self.modifiers["cha"]),
            "Religion":(self.modifiers["int"]),
            "Sleight of Hand":(self.modifiers["dex"]),
            "Stealth":(self.modifiers["dex"]),
            "Survival":(self.modifiers["wis"]),
            }
        self.skillsList = list(self.skills.keys())
        print('Skills Loaded')
        #Add expertise and proficiency bonuses
        if(len(self.proficient)>0):
            for proficiency in self.proficient:
                self.skills[proficiency] = self.skills[proficiency] + self.proficiencyBonus
        if self.joat > 0:
            print('JOAT')
            nonProficient = [x for x in self.skillsList if x not in self.proficient]
            for proficiency in nonProficient:
                self.skills[proficiency] = self.skills[proficiency] + int(self.proficiencyBonus*.5)       
        if(len(self.expertise)>0):       
            for expertise in self.expertise:
                self.skills[expertise] = self.skills[expertise] + self.proficiencyBonus
        print('Skills and Proficiencies Loaded')
        #Saving Throws
        #Needs to save to sheet unforunately

        self.saves = {
            'str':self.modifiers['str'],
            'dex':self.modifiers['dex'],
            'con':self.modifiers['con'],
            'int':self.modifiers['int'],
            'wis':self.modifiers['wis'],
            'cha':self.modifiers['cha']}

        self.saveProficiency = classes[self.charclass][2]
        
        if len(self.xtraSaves) > 0:
            self.saveProficiency.extend(self.xtraSaves)
        
        for save in self.saveProficiency:
            self.saves[save] = self.saves[save] + self.proficiencyBonus
        print('Saves Loaded')
        #FORMAT ALL SKILLS BC THIS SUCKS LMAO
        sLen = 22
            
        
        
        #Initiative
        self.initiative = self.modifiers["dex"]
        #Hitpoints and Hitdie
        if self.charclass != 'NA':
            print('Character Class Set')
            self.hitdie = classes[self.charclass][0]
            print('e')
            self.hitpointMax = (self.hitdie + self.modifiers["con"]) + ((self.level-1) * (int(.5 * self.hitdie)+self.modifiers["con"]+1))
        else:
            self.hitdie = 0
            self.hitpointMax = 0
        print('Hitpoints Calculated')
        self.passivePerception = 10 + self.proficiencyBonus + self.skills['Perception']
        
        #SPELL HELL SPELL HELL SPELL HELLLLLLLLLLLLL
        if classes[self.charclass][3] == 'full':
            self.totalSlots = readCsv('./Stats/FullCaster.csv')[self.level-1]
            #print(self.totalSlots)
        else:
            self.totalSlots = [0,0,0,0,0,0,0,0,0]

            
    def getModifier(self,modifier):
        return(self.modifiers[modifier])
    def getSkill(self,skill):
        return(self.skills[skill])
    def pay(self,amount,type,strict=False):
        return 0
    def recieve(self,amount,type,strict=False):
        return 0
def getSpellSlots(level,castType):
    spellSlots = [0,0,0,0,0,0,0,0,0]
    if castType == 'Full':
        print('hella')
        
        

#pyper = Character.loadCharacter('Fillip Carnere')
#print(pyper)
#pyper.classicConsole()
#print(toad.level,toad.dexterity)
#print(list(pyper.skills.keys())
