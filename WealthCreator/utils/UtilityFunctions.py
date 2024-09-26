async def extract_user_id(mention):
    # Remove the leading <@ and trailing > characters
    mention = mention.strip("<@!>")
    
    # Convert to integer if needed
    return int(mention)
