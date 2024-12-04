from datetime import timedelta


def format_time(seconds):
    """Convert seconds to SRT time format HH:MM:SS,ms."""
    delta = timedelta(seconds=seconds)
    total_seconds = int(delta.total_seconds())
    milliseconds = int((delta.total_seconds() - total_seconds) * 1000)
    return f"{str(delta)[:-3]},{milliseconds:03d}"


def save_transcription(segments_list, output_file):
    """Save transcription segments to an SRT file."""
    with open(output_file, "w") as file:
        for index, segment in enumerate(segments_list, start=1):
            start_time = format_time(float(segment['start'][:-1]))
            end_time = format_time(float(segment['end'][:-1]))
            text = segment['text']

            file.write(f"{index}\n")
            file.write(f"{start_time} --> {end_time}\n")
            file.write(f"{text}\n\n")
