from tests.support import EXPECTED_ROUTES, exercise_all_routes, route_surface


def test_all_original_routes_respond_and_surface_is_preserved():
    application, checked = exercise_all_routes()

    assert route_surface(application) == EXPECTED_ROUTES
    assert len(checked) == len(EXPECTED_ROUTES) + 2
