# create by lesomras on 2026-1-4
from __future__ import annotations
from enum import Enum
from typing import Optional

from .tokens_view import TokensView
from .error_reason import ErrorReason
from miststar.string_operator.node.node_with_type import NodeWithType

class ASTNodeMode(Enum):
    NONE = 0        # 没有向下的分支
    AND = 1         # 有向下的分支，子节点为and关系
    OR = 2          # 有向下的分支，子节点为or关系

class ASTNodeId(Enum):
    NoneId = 0
    NodeJsonAllList = 1
    NodeStringInner = 2
    NodeBlockBlockID = 3
    NodeBlockBlockState = 4
    NodeBlockBlockAndBlockState = 5
    NodeCommandCommandName = 6
    NodeCommandCommand = 7
    NodePositionPositions = 8
    NodePositionPositionsWithError = 9
    NodeRelativeFloatNumber = 10
    NodeRelativeFloatWithError = 11


class ASTNode(object):
    def __init__(self, mode: ASTNodeMode, 
                       node: NodeWithType, 
                       child_nodes: list[ASTNode], 
                       tokens: TokensView, 
                       error_reasons: list[ErrorReason], 
                       ast_node_id: ASTNodeId, 
                       which_best: int = -1) -> None:
        self.mode = mode
        # 一个Node可能会生成多个ASTNode，这些ASTNode使用id进行区分
        self.node = node
        # 子节点为AND类型和OR类型特有
        self.child_nodes = child_nodes
        self.tokens = tokens
        # 不要直接用这个，这里不包括ID错误，只有结构错误，应该用getErrorReason()
        self.error_reasons = error_reasons
        # AST节点ID
        self.ast_node_id = ast_node_id
        # 哪个节点最好，OR类型特有，获取颜色和生成命令格式文本的时候使用
        self.which_best = which_best

    @staticmethod
    def simple_node(node: NodeWithType, 
                    tokens: TokensView, 
                    error_reason: Optional[ErrorReason] = None, 
                    ast_node_id: ASTNodeId = ASTNodeId.NoneId) -> ASTNode:
        if error_reason is None:
            return ASTNode(ASTNodeMode.NONE, node, [], tokens, [], ast_node_id)
        else:
            return ASTNode(ASTNodeMode.NONE, node, [], tokens, [error_reason], ast_node_id)


    @staticmethod
    def and_node(node: NodeWithType, 
                 child_nodes: list[ASTNode], 
                 tokens: TokensView, 
                 error_reason: Optional[ErrorReason] = None, 
                 ast_node_id: ASTNodeId = ASTNodeId.NoneId) -> ASTNode:
        ...

"""
    // TODO 为什么当时我用的是char*，而不是std::shared_ptr<ErrorReason>

    static ASTNode orNode(const Node::NodeWithType &node,
                          std::vector<ASTNode> &&childNodes,
                          const TokensView *tokens,
                          const char16_t *errorReason = nullptr,
                          const ASTNodeId::ASTNodeId &id = ASTNodeId::NONE);


    # 是否有结构错误（不包括ID错误）
    def is_error(self) -> bool:
        return not not self.error_reasons

    def has_child_node(self) -> bool:
        return not not self.child_nodes

    [[nodiscard]] bool isAllSpaceError() const;

    [[nodiscard]] const ASTNode &getBestNode() const;
"""