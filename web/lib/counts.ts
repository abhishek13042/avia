import { Count } from "@/lib/api";

/** The last sample at or before `frame`. Samples are sorted by frame. */
export function countAt(counts: Count[], frame: number): Count | null {
  let found: Count | null = null;
  for (const count of counts) {
    if (count.frame > frame) break;
    found = count;
  }
  return found;
}
