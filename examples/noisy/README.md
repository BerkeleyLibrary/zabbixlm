# Example: Completely random data alongside the real causes

This scenario involves "hiding" the two root cause events in a sea of 25 events generated randomly using Faker.

This initially didn't work. First, the LLM balked at seeing what it thought were Social Security numbers. After those were removed, it still balked at seeing seemingly random data. In both cases it refused to produce a response. A tweak to the system prompt, advising it that it might encounter random data and should press on, caused it to work.
