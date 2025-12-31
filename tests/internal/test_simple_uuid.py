# test 1
from miststar.internal.simple_uuid import new_uuid, UUIDSpace
import pytest

@pytest.fixture
def space() -> UUIDSpace:
    uuid_space: UUIDSpace[str] = UUIDSpace()
    mapping = {
        "f1710238-71e9-4ac1-88f1-2bac3ca0a199": "Bubble Stream",
        "4a829248-f043-4b28-995d-071b208907d0": "Magical Girl",
        "dfa8fd0b-18e7-4ffc-8914-3fe31b354ee0": "Chaos Nya",
    }
    # 为了防止直接调用 UUIDSpace.custom_uuid()
    uuid_space.uuids = set(mapping.keys())
    uuid_space.uuids.add("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")
    uuid_space.free_uuids = {"50efdc87-e5e4-4b9a-8d95-6f1d735bba31"}
    uuid_space.mapping = mapping
    return uuid_space


@pytest.mark.parametrize("uuid, expected", [
    ["50efdc87-e5e4-4b9a-8d95-6f1d735bba31", True],
    ["4a829248-f043-4b28-995d-071b208907d0", True],
    ["c347a9e6-b92f-4f0c-8a04-59343239748d", False],
])
def test_has_uuid(space: UUIDSpace, uuid: str, expected: bool) -> None:
    assert space.has_uuid(uuid) == expected


@pytest.mark.parametrize("uuid, expected", [
    ["50efdc87-e5e4-4b9a-8d95-6f1d735bba31", True],
    ["4a829248-f043-4b28-995d-071b208907d0", False],
])
def test_is_free(space: UUIDSpace, uuid: str, expected: bool) -> None:
    assert space.is_free(uuid) == expected


@pytest.mark.parametrize("uuid, expected", [
    ["50efdc87-e5e4-4b9a-8d95-6f1d735bba31", False],
    ["4a829248-f043-4b28-995d-071b208907d0", True],
])
def test_is_mapped(space: UUIDSpace, uuid: str, expected: bool) -> None:
    assert space.is_mapped(uuid) == expected


def test_generate(space: UUIDSpace) -> None:
    uuid = space.generate()
    assert space.has_uuid(uuid)
    assert space.is_free(uuid)
    assert space.invariant_check()


def test_generate_uuids(space: UUIDSpace) -> None:
    space.generate_uuids(12)
    assert space.invariant_check()


def test_generate_and_custom(space: UUIDSpace) -> None:
    uuid = space.generate_and_custom("The des Alizes")
    assert space.has_uuid(uuid)
    assert space.is_mapped(uuid)
    assert space.invariant_check()


def test_custom(space: UUIDSpace) -> None:
    # case 1 有空闲uuid
    assert space.is_free("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")

    uuid = space.custom("in the petals of snow.")
    assert uuid == "50efdc87-e5e4-4b9a-8d95-6f1d735bba31"
    assert space.is_mapped(uuid)
    assert space.invariant_check()

    # casr 2 无空闲uuid
    uuid2 = space.custom("in the petals of snow.")
    assert space.has_uuid(uuid2)
    assert space.is_mapped(uuid2)
    assert space.invariant_check()


@pytest.mark.parametrize("uuid", [
    "50efdc87-e5e4-4b9a-8d95-6f1d735bba31",
    "491ea0e6-da26-4391-930a-a6c3cc4d3af6"
])
def test_custom_uuid(space: UUIDSpace, uuid: str) -> None:
    space.custom_uuid(uuid, "Saving Gracefully")
    assert space.has_uuid(uuid)
    assert space.is_mapped(uuid)
    assert space.invariant_check()


def test_add_uuid(space: UUIDSpace) -> None:
    # caae 1 已存在
    space.add_uuid("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")
    space.add_uuid("4a829248-f043-4b28-995d-071b208907d0")
    assert space.is_free("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")
    assert space.is_mapped("4a829248-f043-4b28-995d-071b208907d0")

    # case 2 不存在
    assert (not space.has_uuid("c347a9e6-b92f-4f0c-8a04-59343239748d"))
    space.add_uuid("c347a9e6-b92f-4f0c-8a04-59343239748d")
    assert space.has_uuid("c347a9e6-b92f-4f0c-8a04-59343239748d")
    assert space.is_free("c347a9e6-b92f-4f0c-8a04-59343239748d")
    assert space.invariant_check()


def test_forced_free(space: UUIDSpace) -> None:
    # case 1 在 mapping
    value = space.forced_free("4a829248-f043-4b28-995d-071b208907d0")
    assert value == "Magical Girl"
    assert space.has_uuid("4a829248-f043-4b28-995d-071b208907d0")
    assert space.is_free("4a829248-f043-4b28-995d-071b208907d0")
    assert space.invariant_check()

    # case 2 不在 mapping
    dvalue = space.forced_free("c347a9e6-b92f-4f0c-8a04-59343239748d", default = "default")
    assert dvalue == "default"
    assert (not space.has_uuid("c347a9e6-b92f-4f0c-8a04-59343239748d"))

    # case 3 uuid 不在 uuids
    dvalue = space.forced_free("50efdc87-e5e4-4b9a-8d95-6f1d735bba31", default = "default")
    assert dvalue == "default"
    assert space.has_uuid("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")
    assert space.is_free("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")
    assert space.invariant_check()


def test_delete_uuid(space: UUIDSpace) -> None:
    # case 1 在 mapping
    space.delete_uuid("4a829248-f043-4b28-995d-071b208907d0")
    assert (not space.has_uuid("4a829248-f043-4b28-995d-071b208907d0"))
    assert space.invariant_check()

    # case 2 在 free_uuids
    space.delete_uuid("50efdc87-e5e4-4b9a-8d95-6f1d735bba31")
    assert (not space.has_uuid("50efdc87-e5e4-4b9a-8d95-6f1d735bba31"))
    assert space.invariant_check()

    # case 3 不在 uuids
    space.delete_uuid("c347a9e6-b92f-4f0c-8a04-59343239748d")
    assert (not space.has_uuid("c347a9e6-b92f-4f0c-8a04-59343239748d"))
    assert space.invariant_check()