#!/usr/bin/python3
# Python3 program for implementing B+ Tree
# https://www.geeksforgeeks.org/insertion-in-a-b-tree/
# See also visualization https://www.cs.usfca.edu/~galles/visualization/BPlusTree.html

from copy import copy
MAX = 4
NEXT_NODE_NAME = 'A'

# BP node
class Node :

    def __init__(self):
        global NEXT_NODE_NAME
        self.IS_LEAF=False
        self.key, self.size=[None]*MAX,0
        self.ptr=[None]*(MAX+1)
        self.nodeName = NEXT_NODE_NAME
        NEXT_NODE_NAME = chr(ord(NEXT_NODE_NAME)+1)

    def __str__(self):
        " Return a character representation of a node "
        ret_str = f'Node {self.nodeName}: '
        if self.IS_LEAF:
            for key in self.key:
                ret_str +=  f'Data: [{key if key else ""}] '
        else:
            ret_str += f'ptr[{self.ptr[0].nodeName}] '
            for i in range(MAX):
                if not self.key[i]:
                    break
                ret_str += f'key[{self.key[i]}] '
                if self.ptr[i+1]:
                    ret_str += f'ptr[{self.ptr[i+1].nodeName}] '
                else:
                    break
        return ret_str


# BP tree
class BPTree :

# Initialise the BPTree Node
    def __init__(self):
        self.root = None


# Function to find any element
# in B+ Tree
    def search(self,x):

        # If tree is empty
        if (self.root == None) :
            cout << "Tree is empty\n"


        # Traverse to find the value
        else :

            cursor = self.root

            # Till we reach leaf node
            while (not cursor.IS_LEAF) :

                for i in range(cursor.size) :

                    # If the element to be
                    # found is not present
                    if (x < cursor.key[i]) :
                        cursor = cursor.ptr[i]
                        break


                    # If reaches end of the
                    # cursor node
                    if (i == cursor.size - 1) :
                        cursor = cursor.ptr[i + 1]
                        break




            # Traverse the cursor and find
            # the node with value x
            for i in range(cursor.size):

                # If found then return
                if (cursor.key[i] == x) :
                    print("Found")
                    return



            # Else element is not present
            print("Not found")



    # Function to implement the Insert
    # Operation in B+ Tree
    def insert(self, x):

        # If root is None then return
        # newly created node
        if (self.root == None) :
            self.root = Node()
            self.root.key[0] = x
            self.root.IS_LEAF = True
            self.root.size = 1


        # Traverse the B+ Tree
        else :
            cursor = self.root
            parent=None
            # Till cursor reaches the
            # leaf node
            while (not cursor.IS_LEAF) :

                parent = cursor

                for i in range(cursor.size) :

                    # If found the position
                    # where we have to insert
                    # node
                    if (x < cursor.key[i]) :
                        cursor = cursor.ptr[i]
                        break


                    # If reaches the end
                    if (i == cursor.size - 1) :
                        cursor = cursor.ptr[i + 1]
                        break


            if (cursor.size < MAX) :
                i = 0
                while (i < cursor.size and x > cursor.key[i]):
                    i+=1


                for j in range(cursor.size,i,-1):
                    cursor.key[j] = cursor.key[j - 1]


                cursor.key[i] = x
                cursor.size+=1

                cursor.ptr[cursor.size] = cursor.ptr[cursor.size - 1]
                cursor.ptr[cursor.size - 1] = None


            else :

                # Create a newLeaf node
                newLeaf = Node()

                virtualNode=[None]*(MAX + 1)

                # Update cursor to virtual
                # node created
                for i in range(MAX):
                    virtualNode[i] = cursor.key[i]

                i = 0

                # Traverse to find where the new
                # node is to be inserted
                while (i < MAX and x > virtualNode[i]) :
                    i+=1


                # Update the current virtual
                # Node to its previous
                for j in range(MAX,i,-1) :
                    virtualNode[j] = virtualNode[j - 1]


                virtualNode[i] = x
                newLeaf.IS_LEAF = True

                cursor.size = int((MAX + 1) / 2)
                newLeaf.size = MAX + 1 - cursor.size

                cursor.ptr[cursor.size] = newLeaf

                newLeaf.ptr[newLeaf.size] = cursor.ptr[MAX]

                cursor.ptr[MAX] = None

                # Update the current virtual
                # Node's key to its previous
                for i in range(MAX):
                    if i < cursor.size:
                       cursor.key[i] = virtualNode[i]
                    else:
                       cursor.key[i] = 0

                    if i < newLeaf.size:
                        newLeaf.key[i] = virtualNode[i+cursor.size]
                    else:
                        newLeaf.key[i] = 0



                # If cursor is the root node
                if (cursor == self.root) :

                    # Create a new Node
                    newRoot = Node()

                    # Update rest field of
                    # B+ Tree Node
                    newRoot.key[0] = newLeaf.key[0]
                    newRoot.ptr[0] = cursor
                    newRoot.ptr[1] = newLeaf
                    newRoot.IS_LEAF = False
                    newRoot.size = 1
                    self.root = newRoot
                    print(self.root)

                else :

                    # Recursive Call for
                    # insert in internal
                    insertInternal(newLeaf.key[0],
                                parent,
                                newLeaf)





# Function to implement the Insert
# Internal Operation in B+ Tree
def insertInternal(x, cursor, child):

    # If we doesn't have overflow
    if (cursor.size < MAX) :
        i = 0

        # Traverse the child node
        # for current cursor node
        while i < cursor.size and x > cursor.key[i]:
            i+=1


        # Traverse the cursor node
        # and update the current key
        # to its previous node key
        for j in range(cursor.size,i,-1) :

            cursor.key[j] = cursor.key[j - 1]

        # Traverse the cursor node
        # and update the current ptr
        # to its previous node ptr
        for j in range(cursor.size + 1, i + 1,-1):
            cursor.ptr[j] = cursor.ptr[j - 1]


        cursor.key[i] = x
        cursor.size+=1
        cursor.ptr[i + 1] = child


    # For overflow, break the node
    else :

        # For new Interval
        newInternal = Node()
        virtualKey=[None]*(MAX + 1)
        virtualPtr=[None]*(MAX + 2)

        # Insert the current list key
        # of cursor node to virtualKey
        for i in range(MAX) :
            virtualKey[i] = cursor.key[i]


        # Insert the current list ptr
        # of cursor node to virtualPtr
        for i in range(MAX + 1):
            virtualPtr[i] = cursor.ptr[i]


        i = 0

        # Traverse to find where the new
        # node is to be inserted
        while (x > virtualKey[i] and i < MAX) :
            i+=1


        # Traverse the virtualKey node
        # and update the current key
        # to its previous node key
        for j in range(MAX + 1,i,-1):

            virtualKey[j] = virtualKey[j - 1]


        virtualKey[i] = x

        # Traverse the virtualKey node
        # and update the current ptr
        # to its previous node ptr
        for j in range(MAX + 2, i + 1,-1) :
            virtualPtr[j] = virtualPtr[j - 1]


        virtualPtr[i + 1] = child
        newInternal.IS_LEAF = false

        cursor.size = (MAX + 1) / 2

        newInternal.size = MAX - (MAX + 1) / 2

        # Insert new node as an
        # internal node
        j = cursor.size + 1
        for i in range(newInternal.size):
            newInternal.key[i] = virtualKey[j]
            j+=1


        j = cursor.size + 1
        for i in range(newInternal.size):
            newInternal.ptr[i] = virtualKey[j]
            j+=1


        # If cursor is the root node
        if (cursor == self.root) :

            # Create a new root node
            newRoot = self.root

            # Update key value
            newRoot.key[0] = cursor.key[cursor.size]

            # Update rest field of
            # B+ Tree Node
            newRoot.ptr[0] = cursor
            newRoot.ptr[1] = newInternal
            newRoot.IS_LEAF = false
            newRoot.size = 1
            root = newRoot


        else :

            # Recursive Call to insert
            # the data
            insertInternal(cursor.key[cursor.size],
                        findParent(root,
                                    cursor),
                        newInternal)




    # Function to find the parent node
    def findParent(self, cursor, child):
        # If cursor reaches the end of Tree
        if (cursor.IS_LEAF or (cursor.ptr[0]).IS_LEAF) :
            return None


        # Traverse the current node with
        # all its child
        for i in range(cursor.size + 1) :

            # Update the parent for the
            # child Node
            if (cursor.ptr[i] == child) :
                parent = cursor
                return parent


            # Else recursively traverse to
            # find child node
            else :
                parent = findParent(cursor.ptr[i], child)

                # If parent is found, then
                # return that parent node
                if (parent != None):
                    return parent



        # Return parent node
        return parent


    # Function to get the root Node
    def getRoot(self):
        return self.root


# Driver Code
if __name__=='__main__':
    bTree=BPTree()

    # Create B+ Tree
    for i in [1, 4, 9, 10, 11, 12, 13, 15, 16, 20, 25]:
        bTree.insert(i)
        print(f"\nAfter inserting {i}, root is: {bTree.root}")
        yet_to_be_printed = copy(bTree.root.ptr)
        while yet_to_be_printed:
            indexEntry = yet_to_be_printed.pop(0)
            if indexEntry:
                print(indexEntry)
