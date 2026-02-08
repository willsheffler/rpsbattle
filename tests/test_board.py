from sim.board import Board, Position


def test_in_bounds() -> None:
    board = Board(width=3, height=2)
    assert board.in_bounds(Position(0, 0))
    assert board.in_bounds(Position(2, 1))
    assert not board.in_bounds(Position(-1, 1))
    assert not board.in_bounds(Position(3, 1))
    assert not board.in_bounds(Position(1, 2))


def test_clamp() -> None:
    board = Board(width=4, height=5)
    assert board.clamp(Position(-2, 2)) == Position(0, 2)
    assert board.clamp(Position(10, -9)) == Position(3, 0)
    assert board.clamp(Position(1, 3)) == Position(1, 3)
