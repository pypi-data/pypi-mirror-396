class Payload:
    """
    Parses and holds Payload data returned by the blockchain.
    """

    def __init__(self, payload_str: str):
        """
        Initializes a Payload, given a string representation of it.
        :param payload_str: a string representation of the payload returned by the blockchain.
        """
        split_count = payload_str.count("<")

        if split_count < 4:
            raise ValueError(
                "Asset payload must be in the form of "
                "'VER<client_id<comment<root_sig<properties' (v4) or "
                "'VER<client_id<comment<root_uri<last_uri<properties' (v5) -- {}".format(payload_str)
            )

        s = payload_str.split("<")
        self._asset_payload_ver = s[0] or None
        self._client_id = s[1] or None
        self._comment = s[2] or None

        # Handle both NFTv4 and NFTv5 formats
        if split_count == 4:
            # NFTv4 format: VER<client_id<comment<root_sig<properties
            self._root_sig = s[3] or None
            self._root_uri = None
            self._last_uri = None
            self._properties = "<".join(s[4:]) or {}
        elif split_count == 5:
            # NFTv5 format: VER<client_id<comment<root_uri<last_uri<properties
            self._root_uri = s[3] or None
            self._last_uri = s[4] or None
            self._properties = "<".join(s[5:]) or {}
            # For backwards compatibility, extract signature from root_uri if it's a devv:// URI
            if self._root_uri and self._root_uri.startswith("devv://"):
                uri_parts = self._root_uri.split("/")
                if len(uri_parts) >= 5:
                    self._root_sig = "/".join(uri_parts[4:]) if uri_parts[4:] else None  # Extract signature part
                else:
                    self._root_sig = None
            else:
                self._root_sig = self._root_uri  # Fallback if not a proper URI
        else:
            raise ValueError(
                f"Unsupported payload format with {split_count} '<' separators: {payload_str}"
            )

    def __repr__(self):
        payload_repr = (
            f"{self._asset_payload_ver}<{self._client_id}"
            f"<{self._comment}<{self._root_sig}<{self._properties}"
        )
        return payload_repr

    def get_ver(self):
        return self._asset_payload_ver

    def get_client_id(self):
        return self._client_id

    def get_comment(self):
        return self._comment

    def get_root_sig(self):
        return self._root_sig

    def get_root_uri(self):
        return self._root_uri

    def get_last_uri(self):
        return self._last_uri

    def get_properties(self):
        return self._properties
