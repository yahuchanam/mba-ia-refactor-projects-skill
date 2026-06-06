from tests.support import EXPECTED_ROUTES, exercise_all_routes, route_surface


def main():
    application, checked = exercise_all_routes()
    actual_surface = route_surface(application)
    if actual_surface != EXPECTED_ROUTES:
        missing = EXPECTED_ROUTES - actual_surface
        extra = actual_surface - EXPECTED_ROUTES
        raise RuntimeError(f"Route mismatch. Missing={missing}; extra={extra}")

    print(f"Verified {len(EXPECTED_ROUTES)} original endpoints.")
    print(f"Completed {len(checked)} response checks, including authorization.")


if __name__ == "__main__":
    main()
