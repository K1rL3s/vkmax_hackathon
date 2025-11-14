import {
  CellHeader,
  CellList,
  CellSimple,
  Flex,
  Input,
  Typography,
} from '@maxhub/max-ui'
import { Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Modal } from './ui/modal'
import { TIMEZONES } from '@/constants'

export type Timezone = {
  label: string
  value: number
}

type TimezoneSelectModalProps = {
  onSelect: (timezone: Timezone) => void
  isOpen: boolean
  onClose: () => void
}

export function TimezoneSelectModal({
  onSelect,
  isOpen,
  onClose,
}: TimezoneSelectModalProps) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    return TIMEZONES.filter((timezone) =>
      timezone.label.toLowerCase().includes(query.toLowerCase()),
    )
  }, [query])

  const grouped = useMemo(() => {
    return filtered.reduce(
      (acc: { [key: string]: Array<Timezone> | undefined }, tz) => {
        const key = tz.label.charAt(0).toUpperCase()
        if (!acc[key]) {
          acc[key] = []
        }
        acc[key].push(tz)
        return acc
      },
      {},
    )
  }, [filtered])

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="w-full h-full">
      <Flex
        className="py-2 px-2 h-full"
        direction="column"
        align="center"
        gapY={24}
      >
        <Input
          compact={false}
          className="w-full shrink-0"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          iconBefore={<Search size={18} />}
        />
        <Flex direction="column" className="grow w-full overflow-y-scroll">
          <div className="max-h-0 w-full">
            {Object.entries(grouped)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([letter, timezones]) => (
                <CellList
                  mode="island"
                  className="mb-4"
                  filled
                  header={
                    <CellHeader className="pb-2!">
                      <Typography.Title variant="large-strong">
                        {letter}
                      </Typography.Title>
                    </CellHeader>
                  }
                >
                  {timezones?.map((tz) => (
                    <CellSimple
                      key={tz.value}
                      onClick={() => {
                        onSelect(tz)
                        onClose()
                      }}
                      showChevron
                    >
                      {tz.label}
                    </CellSimple>
                  ))}
                </CellList>
              ))}
          </div>
        </Flex>
      </Flex>
    </Modal>
  )
}
