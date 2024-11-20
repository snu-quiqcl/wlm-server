from operation.models import Operation

def get_running_status(ch: int) -> tuple[bool, bool]:
    """Gets running status of WLM and the given channel based on operation DB.
    
    Args:
        ch: Target channel.

    Returns:
        Tuple with WLM running status and target channel running status.
    """
    latest_operations = (
        Operation.objects.order_by('channel', 'user', '-occured_at').distinct('channel', 'user')
    )  # latest operations for each channel and user
    on_operations = latest_operations.filter(on=True)
    is_wlm_running = on_operations.exists()
    is_channel_running = on_operations.filter(channel__channel=ch).exists()
    return is_wlm_running, is_channel_running
