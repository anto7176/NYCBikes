import { z } from "zod";
import * as L from 'leaflet';

export const ItinerarySchema = z.object({
  positions: z.array(z.custom<L.LatLngTuple>()).max(2),
  start_station_name: z.string().nullable().optional(),
  end_station_name: z.string().nullable().optional(),
  nb_acc: z.number().nullable().optional(),
  color: z.string().optional().nullable(),
  popup_text: z.string().optional().nullable(),
});

export type Itinerary = z.infer<typeof ItinerarySchema>;