import z from "zod";

export const ChartDataSchema = z.object({
  labels: z.array(z.string()),
  datasets: z.array(z.object({
    label: z.string(),
    data: z.array(z.number()),
    backgroundColor: z.array(z.string()),
    borderColor: z.array(z.string()),
    borderWidth: z.number().nullable().catch(1).default(1),
  })),
});

export type ChartData = z.infer<typeof ChartDataSchema>;