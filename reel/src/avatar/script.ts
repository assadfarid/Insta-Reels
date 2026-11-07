// Script for the presenter reel. Timings are ESTIMATES (about 2.7 words per second) until the real
// voiceover exists: replace `start`/`end` (seconds) with the actual clip timings and re-render.
export type Line = {
  text: string;
  start: number;
  end: number;
  keys: string[];
  card: number;
};

export const LINES: Line[] = [
  {
    text: "This luxury real-estate site took me days, not weeks. Here's the workflow.",
    start: 0.5,
    end: 5.1,
    keys: ["days,", "workflow."],
    card: 0,
  },
  {
    text: "First, I start from the client's voice, not from a template.",
    start: 5.5,
    end: 9.7,
    keys: ["voice,", "template."],
    card: 1,
  },
  {
    text: "Then I design the sections: a manifesto, four projects and a private consultation form.",
    start: 10.1,
    end: 15.1,
    keys: ["manifesto,", "projects", "form."],
    card: 2,
  },
  {
    text: "I build it natively in WordPress, so the client can edit everything.",
    start: 15.5,
    end: 20.0,
    keys: ["WordPress,", "edit"],
    card: 3,
  },
  {
    text: "Then I test it on a phone, because that's where buyers look first.",
    start: 20.4,
    end: 24.9,
    keys: ["phone,", "first."],
    card: 4,
  },
  {
    text: "Want the exact workflow? Comment WORKFLOW and I'll send it.",
    start: 25.3,
    end: 29.1,
    keys: ["workflow?", "WORKFLOW"],
    card: 5,
  },
];

export const KEYWORD = "WORKFLOW";
export const DURATION_S = 32;
