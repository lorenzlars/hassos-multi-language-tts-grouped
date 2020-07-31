string_format = "{sentence} {groups}"
xml_body_format = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xml:lang=\"en-US\">{content}</speak>"
xml_voice_format = "<voice name=\"{name}\">{content}</voice>"
xml_break_format = "<break time=\"{time}\" />"
voices = {
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural"
}


entity_id = data.get("entity_id")
translations = data.get("translations")
groups = data.get("groups")
alternative = data.get("alternative")
delay = data.get("delay")


# Filter to get only active groups
def filter_groups(groups):
    filtered_groups = []

    for group in groups:
        for sensor in group['entities']:
            if hass.states.get(sensor).state == 'on':
                filtered_groups.append(group)
                break

    return filtered_groups


# Generate the string of the concatinated names for the groups based on a language
def build_group_string(groups, language):
    strings = []

    for group in groups:
        strings.append(group['translations'][language])

    return ", ".join(strings)


# Build the strings for all languages
def build_strings(groups, translations):
    full_translations = translations

    for key, value in translations.items():
        sensor_string = build_group_string(groups, key)
        full_translations[key] = string_format.format(
            sentence=value, groups=sensor_string)

    return full_translations


def build_ssml(strings):
    first = True
    body = ""

    for key, value in strings.items():
        if first:
            first = False
            if delay is not None:
                value = xml_break_format.format(time=delay) + value

        body = body + \
            xml_voice_format.format(
                name=voices[key], content=value)

    return xml_body_format.format(content=body)


filtered_groups = filter_groups(groups)

if len(filtered_groups) > 0:
    hass.services.call("tts", "microsoft_ssml_say", {
        "entity_id": entity_id,
        "message": build_ssml(build_strings(filtered_groups, translations))}, False)
elif alternative is not None:
    hass.services.call("tts", "microsoft_ssml_say", {
        "entity_id": entity_id,
        "message": build_ssml(alternative)}, False)
