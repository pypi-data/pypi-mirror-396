# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def calculate_adam_beta_gain(adam_beta_one: float, adam_beta_two: float) -> float:
    """
    Utility function expressing relationship between adam parameters and beta gain.
    """
    return (adam_beta_two - adam_beta_one) / (1 - adam_beta_one)


def calculate_adam_beta_two(adam_beta_one: float, adam_beta_gain: float) -> float:
    """
    Utility function inverting the relationship between adam parameters and beta gain.
    """
    return (1 - adam_beta_one) * adam_beta_gain + adam_beta_one
