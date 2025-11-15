import parser from 'cron-parser'

import type { EventResponse } from '../api/gen.schemas'
import type { CalendarEvent } from '@/components/event/event-list'
import { TIMEZONES } from '@/constants'

export function expandCronEvents(
  events: Array<EventResponse>,
  startDate: Date,
  endDate: Date,
  timezoneOffset: number,
): Array<CalendarEvent> {
  const result: Array<CalendarEvent> = []

  for (const ev of events) {
    try {
      const options = {
        currentDate: startDate,
        endDate,
        iterator: true,
        tz: TIMEZONES.find((tz) => tz.value === timezoneOffset)?.tz,
      }

      const interval = parser.parse(ev.cron, options)

      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      while (true) {
        try {
          const obj = interval.next()
          result.push({
            id: ev.id,
            title: ev.title,
            date: obj.toDate(),
            type: ev.type === 'message' ? 'message' : 'event',
          })
        } catch {
          break
        }
      }
    } catch (err) {
      console.error('Error expanding cron events:', err)
    }
  }

  return result.sort((a, b) => a.date.getTime() - b.date.getTime())
}
