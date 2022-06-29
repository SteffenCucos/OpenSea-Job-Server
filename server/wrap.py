import math


def word_wrap_3(text: str, line_length) -> str:
    wrapped_text = ""
    words = text.split(" ")
    # Reverse the words so we can efficiently pop off the next word
    words.reverse()

    budget = line_length
    curLine = ""
    while(len(words)):
        word = words.pop()

        # Check if we have space to add the word
        if budget - len(word) >= 0:
            budget -= len(word)



def word_wrap(line,lengthLine):
    print("#"*lengthLine)
    inserts = []
    for n in range(len(line)):
        if n%lengthLine == 0 and n!=0:
            #find the first white space behind n
            index = n
            if(not line[n].isspace()):
                for i in range(n-lengthLine,n,1):
                    if line[i].isspace():
                        index = i
            inserts.append(index)
            
    inserts.reverse()
    for index in inserts:
        line = line[:index] + "\n" + line[index:]

    lines = line.split("\n")
    newLine = ""
    for l in lines:
        if len(l) and l[0].isspace():
            l = l[1:]
        newLine += l+"\n"
    return newLine

word = '''
In mathematics, a group is a set equipped with an operation that combines any two elements of the set to produce a third element of the set, in such a way that the operation is associative, an identity element exists and every element has an inverse. These three conditions, called group axioms, hold for number systems and many other mathematical structures. For example, the integers together with the addition operation form a group. The concept of a group and its definition through the group axioms was elaborated for handling, in a unified way, essential structural properties of entities of very different mathematical nature (such as numbers, geometric shapes and polynomial roots). Because of the ubiquity of groups in numerous areas (both within and outside mathematics), some authors consider them as a central organizing principle of contemporary mathematics.[1][2]
Groups arise naturally in geometry for the study of symmetries and geometric transformations: the symmetries of an object form a group, called the symmetry group of the object, and the transformations of a given type form generally a group. These examples were at the origin of the concept of group (together with Galois groups). Lie groups arise as symmetry groups in geometry but appear also in the Standard Model of particle physics. The Poincaré group is a Lie group consisting of the symmetries of spacetime in special relativity. Point groups describe symmetry in molecular chemistry.
The concept of a group arose from the study of polynomial equations, starting with Évariste Galois in the 1830s, who introduced the term group (groupe, in French) for the symmetry group of the roots of an equation, now called a Galois group. After contributions from other fields such as number theory and geometry, the group notion was generalized and firmly established around 1870. Modern group theory—an active mathematical discipline—studies groups in their own right. To explore groups, mathematicians have devised various notions to break groups into smaller, better-understandable pieces, such as subgroups, quotient groups and simple groups. In addition to their abstract properties, group theorists also study the different ways in which a group can be expressed concretely, both from a point of view of representation theory (that is, through the representations of the group) and of computational group theory. A theory has been developed for finite groups, which culminated with the classification of finite simple groups, completed in 2004. Since the mid-1980s, geometric group theory, which studies finitely generated groups as geometric objects, has become an active area in group theory.'''

word = '''
The concept of a group arose from the study of polynomial equations, starting with Évariste Galois in the 1830s, who introduced the term group (groupe, in French) for the symmetry group of the roots of an equation, now called a Galois group. After contributions from other fields such as number theory and geometry, the group notion was generalized and firmly established around 1870. Modern group theory—an active mathematical discipline—studies groups in their own right. To explore groups, mathematicians have devised various notions to break groups into smaller, better-understandable pieces, such as subgroups, quotient groups and simple groups. In addition to their abstract properties, group theorists also study the different ways in which a group can be expressed concretely, both from a point of view of representation theory (that is, through the representations of the group) and of computational group theory. A theory has been developed for finite groups, which culminated with the classification of finite simple groups, completed in 2004. Since the mid-1980s, geometric group theory, which studies finitely generated groups as geometric objects, has become an active area in group theory.
'''
print(word_wrap(word, 80))