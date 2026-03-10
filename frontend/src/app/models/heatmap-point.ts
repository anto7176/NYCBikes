import { z } from "zod";

export const HeatmapPointSchema = z.object({
  lat: z.number(),
  lng: z.number(),
  count: z.number().default(1),
});

export type HeatmapPoint = z.infer<typeof HeatmapPointSchema>;