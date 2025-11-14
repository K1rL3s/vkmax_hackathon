import { useMemo, useState } from 'react'
import {
  Button,
  CellList,
  CellSimple,
  Flex,
  Input,
  Typography,
} from '@maxhub/max-ui'
import { Search } from 'lucide-react'
import clsx from 'clsx'
import { Modal } from '../ui/modal'
import { Avatar } from '../avatar'
import type { GroupUserItem } from '@/lib/api/gen.schemas'

type ParticipantSelectModalProps = {
  onSelect: (participantId: number) => void
  isOpen: boolean
  onClose: () => void
  options: Array<GroupUserItem>
  value: Array<number>
}

export function ParticipantSelectModal({
  onSelect,
  value,
  isOpen,
  options,
  onClose,
}: ParticipantSelectModalProps) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    return options.filter((option) =>
      option.firstName?.toString().toLowerCase().includes(query.toLowerCase()),
    )
  }, [options, query])

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="w-full h-full">
      <Flex
        className={'py-2 px-2 h-full'}
        direction="column"
        align="center"
        gapY={24}
      >
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full shrink-0"
          iconBefore={<Search size={18} />}
          placeholder="Поиск участников"
        />

        <div className="w-full h-full grow overflow-y-auto rounded-3xl">
          <div className="max-h-0">
            <CellList>
              {filtered.map((opt) => (
                <>
                  <CellSimple
                    onClick={() => onSelect(opt.userId)}
                    before={
                      <div
                        className={clsx(
                          'size-6 border-2 border-gray-300/40 rounded-full flex items-center justify-center',
                        )}
                      >
                        <div
                          className={clsx(
                            'size-3 bg-gray-300/40 rounded-full transition-opacity',
                            {
                              'opacity-100!': value.includes(opt.userId),
                            },
                            {
                              'opacity-0': !value.includes(opt.userId),
                            },
                          )}
                        />
                      </div>
                    }
                  >
                    <Flex align="center" gapX={18}>
                      <Avatar
                        className="shrink-0"
                        size={28}
                        firstName={opt.firstName?.toString()}
                        lastName={opt.lastName?.toString()}
                      />
                      <Typography.Title>
                        {opt.firstName} {opt.lastName}
                      </Typography.Title>
                    </Flex>
                  </CellSimple>
                </>
              ))}
            </CellList>
          </div>
        </div>
        <Button
          appearance="themed"
          mode="secondary"
          className="w-full"
          onClick={onClose}
        >
          Закрыть
        </Button>
      </Flex>
    </Modal>
  )
}
