"""
对嵌套三运组进行修改，本文件的函数供triple.py使用
"""
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def modifyNotImply(s="") -> str:
    triple = s

    def changeTree(root: TreeNode):
        """
        (A,不导致,B)  =>  (A,导致,(无:否定词,否定修饰,B))
        """
        if root is None:
            return None
        if root.val == "不导致":
            root.val = "导致"
            temp = TreeNode("否定修饰")
            temp.left = TreeNode("无:否定词")
            temp.right = root.right
            root.right = temp
        root.left = changeTree(root.left)
        root.right = changeTree(root.right)
        return root

    if "不导致" in triple:
        root = buildTree(triple)
        root = changeTree(root)
        triple = stringTree(root)
    # print(triple)
    return triple

def modifyParallel2Two(s="") -> [str]:
    '''
    (a,predicate,(x,或/与/并列,y))　　－> (a,predicate,x),(a,predicate,y)
    ((x,或/与/并列,y),predicate,a)　　－> (x,predicate,a),(y,predicate,a)
    '''
    if s:
        triple = s
    else: 
        return []
        
    def changeTree(root1: TreeNode, root2: TreeNode, changed: bool) -> None:
        # 将两棵一样的树 中的并列的左 右支分别分给两棵树
        if not root1 or changed: return
        if root1.left and root1.left.val in ["并列"]:
            root2.left = root1.left.right
            root1.left = root1.left.left
            changed = True
        if not changed and root1.right and root1.right.val in ["并列"]:
            root2.right = root1.right.right
            root1.right = root1.right.left
            changed = True
        changeTree(root1.left, root2.left, changed)
        changeTree(root1.right, root2.right, changed)
        return

    if "并列" in triple:
        root1 = buildTree(triple)
        root2 = buildTree(triple)
        changed = False
        changeTree(root1, root2, changed)
        triples = modifyParallel2Two( stringTree(root1) ) + modifyParallel2Two( stringTree(root2) )
    else:
        triples = [triple]
    # print(triple)
    return triples


def modifyParallel(s="") -> str:
    """
    将并列树改成 (···((A,并列,B),并列,C)···,并列,N)
    """
    if s:
        triple = s

    def buildTree(triple: str) -> TreeNode:
        # triple : (A,并列,B)
        if triple is None:
            return None
        if "并列" not in triple:
            return TreeNode(triple)
        beginA, endA = 1, -1
        beginB, endB = -1, len(triple) - 1
        count = 0
        if triple[1] == "(":
            for i in range(1, len(triple)):
                if triple[i] == "(":
                    count += 1
                elif triple[i] == ")":
                    count -= 1
                    if count == 0:
                        endA = i + 1
                        break
        else:
            endA = triple.find(",")
        beginB = endA + 1 + triple[endA + 1 :].find(",") + 1
        # print(triple[beginA:endA], triple[beginB:endB])
        root = TreeNode(triple[endA + 1 : beginB - 1])
        root.left = buildTree(triple[beginA:endA])
        root.right = buildTree(triple[beginB:endB])
        return root

    def dfs(root: TreeNode) -> list:
        if root is None:
            return []
        res = []
        if root.left is None and root.right is None:
            res.append(root)
            return res
        if root.val != "并列":
            res.append(root)
            return res
        res += dfs(root.left)
        res += dfs(root.right)
        return res

    def buildFormalTree(nodes: list) -> TreeNode:
        if len(nodes) == 0:
            return None
        if len(nodes) == 1:
            return nodes[0]
        if len(nodes) == 2:
            root = TreeNode("并列")
            root.left = nodes[0]
            root.right = nodes[1]
        root = TreeNode("并列")
        root.left = nodes[0]
        root.right = buildFormalTree(nodes[1:])
        return root

    def changeTree(root: TreeNode):
        if root is None:
            return None
        if root.val == "并列":
            leaves = dfs(root)
            root = buildFormalTree(leaves)
        root.left = changeTree(root.left)
        root.right = changeTree(root.right)
        return root

    if "并列" in triple:
        root = buildTree(triple)
        root = changeTree(root)
        triple = stringTree(root)
    # print(triple)
    return triple


def modifyCheck(s=""):
    triple = s

    def changeTree(root: TreeNode):
        """
        ((A,导致,B),条件为,C) -> (A,导致,(B,条件为,C))
        """
        if root is None:
            return None
        if root.val == "条件为" and root.left.val == "导致":
            A = root.left.left
            B = root.left.right
            C = root.right
            root.val = "导致"
            root.left = A
            root.right = TreeNode("条件为")
            root.right.left = B
            root.right.right = C
        root.left = changeTree(root.left)
        root.right = changeTree(root.right)
        return root

    if "条件为" in triple and "导致" in triple:
        # print(triple)
        root = buildTree(triple)
        root = changeTree(root)
        triple = stringTree(root)
    return triple

def modifyModification(s=""):
    triple = s

    def changeTree(root: TreeNode):
        """
        (A,修饰限定,B:修饰语) -> (B:修饰语,修饰限定,A)  其中A不是修饰语
        """
        if root is None:
            return None
        modification = ["修饰语", "状态修饰语", "性质修饰语", "程度修饰语", "频率修饰语", "方位修饰语", "数量修饰语"]
        if (
            root.val == "修饰限定"
            and root.right.val.split(":")[-1] in modification
            and root.left.val.split(":")[-1] not in modification
        ):
            # if root.val == '修饰限定' and root.right.val in modification and root.left.val not in modification:
            temp = TreeNode("修饰限定")
            temp.left = root.right
            temp.right = root.left
            root = temp
        root.left = changeTree(root.left)
        root.right = changeTree(root.right)
        return root

    # if '执行检查' in triple:
    #     print(triple)
    if "修饰限定" in triple:
        # print(triple)
        root = buildTree(triple)
        root = changeTree(root)
        triple = stringTree(root)
    return triple

def buildTree(triple: str) -> TreeNode:
    # triple : (A,并列,B)
    if triple is None:
        return None
    if "," not in triple:
        return TreeNode(triple)
    beginA, endA = 1, -1
    beginB, endB = -1, len(triple) - 1
    count = 0
    if triple[1] == "(":
        for i in range(1, len(triple)):
            if triple[i] == "(":
                count += 1
            elif triple[i] == ")":
                count -= 1
                if count == 0:
                    endA = i + 1
                    break
    else:
        endA = triple.find(",")
    beginB = endA + 1 + triple[endA + 1 :].find(",") + 1
    # print(triple[beginA:endA], triple[beginB:endB])
    root = TreeNode(triple[endA + 1 : beginB - 1])
    root.left = buildTree(triple[beginA:endA])
    root.right = buildTree(triple[beginB:endB])
    return root

def stringTree(root: TreeNode) -> str:
    if not root:
        return ""
    if not root.left and not root.right:
        return root.val
    return (
        "("
        + stringTree(root.left)
        + ","
        + root.val
        + ","
        + stringTree(root.right)
        + ")"
    )

if __name__ == "__main__":
    triple = "(心源性哮喘:疾病,导致,(((气急:症状,并列,端坐呼吸:症状),并列,阵发性咳嗽:症状),并列,咳出粉红色泡沫痰:症状))"
    triple = "(慢性嗜酸粒细胞性肺炎:疾病,导致,(((((呼吸困难:症状,并列,咳嗽:症状),并列,发热:症状),并列,盗汗:症状),并列,体重减轻:症状),并列,喘鸣:症状))"
    triple = "(((急性嗜酸粒细胞性肺炎:疾病,并列,慢性嗜酸粒细胞性肺炎:疾病),并列,变应性肉芽肿血管炎:疾病),导致,嗜酸粒细胞性肺炎:疾病)"
    triples = modifyParallel2Two(triple)
    print(triples)