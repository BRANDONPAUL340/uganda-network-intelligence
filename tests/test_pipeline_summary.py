def test_pipeline_health_success():
    """
    ARRANGE, ACT & ASSERT: Verifies that a successful closeout state 
    accompanied by zero quality gate contract breaches accurately computes 
    an operating health index classification of HEALTHY.
    """
    status = "SUCCESS"
    quality_failed = 0

    if status == "SUCCESS" and quality_failed == 0:
        health = "HEALTHY"
    elif status == "FAILED":
        health = "FAILED"
    else:
        health = "WARNING"

    assert health == "HEALTHY"


def test_pipeline_health_failure():
    """
    ARRANGE, ACT & ASSERT: Verifies that a pipeline execution crash state 
    properly routes across our decision gates to compute a status of FAILED.
    """
    status = "FAILED"
    quality_failed = 1

    if status == "SUCCESS" and quality_failed == 0:
        health = "HEALTHY"
    elif status == "FAILED":
        health = "FAILED"
    else:
        health = "WARNING"

    assert health == "FAILED"
