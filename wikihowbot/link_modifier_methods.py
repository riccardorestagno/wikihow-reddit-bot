import re
import requests
from bs4 import BeautifulSoup
from enum import Enum


class AmpType(Enum):
    rel = 1
    can_url = 2
    redirect = 3


def link_formatter(comment, post_reapproval=False):
    """Formats user-provided url to a plain-text desktop link, if not properly formatted."""
    comment_to_reply = ""

    links = re.findall("(?P<url>https?://[^\s]+)", comment)
    if links:
        link = links[0].split('](', 1)[0].rsplit(')', 1)[0]
    else:
        return comment_to_reply

    if is_url_amp(link):
        non_amp_link = get_canonical(link.replace('m.wikihow', 'www.wikihow'))
        if non_amp_link:
            comment_to_reply = 'Non-AMP link: ' + non_amp_link
            link = non_amp_link

    if 'm.wikihow' in link:
        comment_to_reply = 'Desktop link: ' + link.replace('m.wikihow', 'www.wikihow')
    elif '](' in comment and link not in comment.split('](')[0]:
        comment_to_reply = 'Plain-text link: ' + link
    elif link != comment and post_reapproval:
        return 'User-provided source: ' + link

    if comment_to_reply and post_reapproval:
        comment_to_reply = 'User-provided source: ' + comment_to_reply.split(': ')[1]

    return comment_to_reply


# All methods below were taken from/inspired by the source code of AmputatorBot - A Reddit bot which replies to all AMP links with desktop links.
# Source code: https://github.com/KilledMufasa/AmputatorBot
# Original author: Killed_Mufasa
def soup_session(url):
    try:
        session = requests.Session()
        amp_link = session.get(url)
        return BeautifulSoup(amp_link.content, "html.parser")
    # If the submitted page couldn't be fetched, return None.
    except (ConnectionError, Exception):
        return None


def is_url_amp(link):
    link = link.lower()  # Make link lowercase.

    # If the string contains an AMP link, return True.
    if "/amp" in link or "amp/" in link or ".amp" in link or "amp." in link or "?amp" in link \
            or "amp?" in link or "=amp" in link or "amp=" in link or "&amp" in link or "amp&" in link \
            and "https://" in link:
        return True

    # If no AMP link was found in the string, return False.
    return False


def get_canonical(original_url, depth=3):
    """Finds desktop URL from AMP URL, if possible."""

    next_url = original_url

    # Try for every AMP link type, until the max is reached.
    for _ in range(depth):
        for amp_type in [AmpType.rel, AmpType.can_url, AmpType.redirect]:
            # Get the HTML content of the webpage.
            soup = soup_session(next_url)
            if soup is None:
                return None
            # Try to find the canonical url.
            found_canonical_link, is_solved = get_canonical_link(amp_type, soup, original_url)
            # If the canonical url returned is not AMP, save and return it.
            if is_solved:
                return found_canonical_link

            # If the canonical returned is still AMP, try again with next AMP link type.
            if found_canonical_link:
                next_url = found_canonical_link
                break

    return None


def get_canonical_link(amp_type, soup, url):
    if amp_type == AmpType.rel:
        return get_canonical_with_rel(soup, url)
    elif amp_type == AmpType.can_url:
        return get_canonical_with_canurl(soup, url)
    elif amp_type == AmpType.redirect:
        return get_canonical_with_redirect(soup, url)

    return None, False


def get_canonical_with_rel(soup, url):
    # Get all canonical links in a list using rel
    try:
        canonical_links = soup.find_all(rel='canonical')
        if canonical_links:
            for link in canonical_links:
                # Get the direct link
                found_canonical_url = link.get('href')
                # If the canonical url is the submitted url, don't use it.
                if found_canonical_url != url:
                    if not is_url_amp(found_canonical_url):
                        return found_canonical_url, True
                    else:
                        return found_canonical_url, False

    except requests.exceptions.RequestException:
        pass

    return None, False


def get_canonical_with_canurl(soup, url):
    # Get all canonical links in a list using rel.
    try:
        canonical_links = soup.find_all(a='amp-canurl')
        if canonical_links:
            for a in canonical_links:
                # Get the direct link
                found_canonical_url = a.get('href')
                # If the canonical url is the submitted url, don't use it.
                if found_canonical_url != url:
                    if not is_url_amp(found_canonical_url):
                        return found_canonical_url, True
                    else:
                        return found_canonical_url, False

    except requests.exceptions.RequestException:
        pass

    return None, False


def get_canonical_with_redirect(soup, url):
    try:
        content = soup.get_text().lower()
        # Try to detect if the page has a Redirect Notice.
        if "redirect notice" in content or "The page you were on is trying to send you to" in content:
            redirect_link = soup.find_all('a')[0].get('href')
            if redirect_link != url:
                if not is_url_amp(redirect_link):
                    return redirect_link, True
                else:
                    return redirect_link, False

    except requests.exceptions.RequestException:
        pass

    return None, False
