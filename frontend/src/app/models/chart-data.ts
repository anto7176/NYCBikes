import z from "zod";

export const ChatDataSchema = z.object({
  labels: z.array(z.string()),
  datasets: z.array(z.object({
    label: z.string(),
    data: z.array(z.number()),
    backgroundColor: z.array(z.string()),
    borderColor: z.array(z.string()),
    borderWidth: z.number().nullable().catch(1).default(1),
  })),
});

export type ChatData = z.infer<typeof ChatDataSchema>;