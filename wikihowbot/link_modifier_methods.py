import re


def link_formatter(comment, post_reapproval=False):
    """Formats user-provided url to a plain-text desktop link, if not properly formatted."""
    comment_to_reply = ""

    links = re.findall("(?P<url>https?://[^\s]+)", comment)
    if links:
        link = links[0].split('](', 1)[0].rsplit(')', 1)[0]
    else:
        return comment_to_reply

    if is_url_amp(link):
        link = convert_amp_link_to_standard_format(link)
        comment_to_reply = 'Non-AMP link: ' + link

    if 'm.wikihow' in link:
        link = link.replace('m.wikihow', 'www.wikihow')
        comment_to_reply = 'Desktop link: ' + link
    elif '](' in comment and link not in comment.split('](')[0]:
        comment_to_reply = 'Plain-text link: ' + link

    if post_reapproval:
        comment_to_reply = 'User-provided source: ' + link

    return comment_to_reply


def convert_amp_link_to_standard_format(link):
    non_amp_link = link.split('?', 1)[0]
    url_prefix = non_amp_link.split('.wikihow.')[0].rsplit('/', 1)[1]

    return f"https://{url_prefix}.wikihow.{non_amp_link.split('.wikihow.')[1]}"


def is_url_amp(link):
    link = link.lower()  # Make link lowercase.

    # If the string contains an AMP link, return True.
    if "/amp" in link or "amp/" in link or ".amp" in link or "amp." in link or "?amp" in link \
            or "amp?" in link or "=amp" in link or "amp=" in link or "&amp" in link or "amp&" in link \
            and "https://" in link:
        return True

    # If no AMP link was found in the string, return False.
    return False
