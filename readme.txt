essentially an implementation of this:

    user {
        my_class name: String
        my_other_class video_count: count(videos)
        my_class videos: []video
    }

    video {
        ...
    }