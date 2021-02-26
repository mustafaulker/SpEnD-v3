class Filter:

    # Default list to filtering wanted keywords in crawled links
    default_wanted_keys = ['sparql', 'query', 'endpoint', 'rdf', 'linkeddata', 'opendata']

    # Default list to filtering unwanted keywords in crawled links
    default_unwanted_keys = ['.html', 'pdf', 'txt', 'tutorial', 'tip', 'hint', 'wikipedia',
                             'stackoverflow', 'how-to', 'faq', 'learning', 'www.w3.org', 'medium.com']

    @staticmethod
    def filter_wanted_keywords(links, wanted_keys=default_wanted_keys):
        """
        Filter out wanted links in the search results.
        Rest of the links will not be checked for Endpoint.

        :param links: Search result links list.
        :param wanted_keys: Keywords to be applied as a filter to keep links that contains wanted keywords.
        :return: Filtered links set.
        """
        wanted_links = []
        for filter_word in wanted_keys:
            for link in links:
                if filter_word in link.lower():
                    wanted_links.append(link)
        return set(wanted_links)

    @staticmethod
    def filter_unwanted_keywords(links, unwanted_keys=default_unwanted_keys):
        """
        Filter out wanted links in the search results.
        Links which contains unwanted keywords, will be deleted from results.

        :param links: Search result links list.
        :param unwanted_keys: Keywords to be applied as a filter to remove links that contains unwanted keywords.
        :return: Filtered links set.
        """
        unwanted_links = []
        for filter_word in unwanted_keys:
            for link in links:
                if filter_word in link.lower():
                    unwanted_links.append(link)
        return set(links) - set(unwanted_links)

    @staticmethod
    def filter_suffix(links, suffix='?help'):
        """
        Filter out unwanted suffixes in the search results.

        :param links: Search result links list.
        :param suffix: Link suffixes to be deleted.
        :return: Filtered links set
        """
        arranged_link, to_remove = [], []
        for link in links:
            if suffix in link.lower():
                to_remove.append(link)
                arranged_link.append(link.split(suffix)[0])

        return set(list(links) + arranged_link) - set(to_remove)

    @staticmethod
    def triple_filtering(links, wanted_keys=default_wanted_keys, unwanted_keys=default_unwanted_keys, suffix='?help'):
        """
        Method to use wanted/unwanted/suffix methods at once.

        :param links: Search result links list.
        :param wanted_keys: Keywords to be applied as a filter to keep links that contains wanted keywords.
        :param unwanted_keys: Keywords to be applied as a filter to remove links that contains unwanted keywords.
        :param suffix: Link suffixes to be deleted.
        :return: Filtered search result links.
        """
        return Filter.filter_suffix(
            Filter.filter_unwanted_keywords(
                Filter.filter_wanted_keywords(links, wanted_keys), unwanted_keys), suffix)
