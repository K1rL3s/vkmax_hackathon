import clsx from 'clsx'
import { CellAction, CellList, Flex } from '@maxhub/max-ui'

export type Option = {
  label: string
  id: number
}

type RatioInputProps = {
  onChange: (option: Option) => void
  value: number
  options: Array<Option>
  className?: string
  header?: React.ReactNode
}

export function RatioInput({
  options,
  value,
  onChange,
  className,
  header,
}: RatioInputProps) {
  return (
    <div className={clsx('w-full', className)}>
      <Flex direction="column" gapY={12}>
        <CellList header={<div className="pl-5 pb-3">{header}</div>}>
          {options.map((opt, id) => (
            <>
              <CellAction
                mode="primary"
                onClick={() => onChange(opt)}
                innerClassNames={{ content: 'text-(--text-primary)' }}
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
                          'opacity-100!': opt.id === value,
                        },
                        {
                          'opacity-0': opt.id !== value,
                        },
                      )}
                    />
                  </div>
                }
              >
                {opt.label}
              </CellAction>
              {id !== options.length - 1 && (
                <div className="border-b border-gray-300/10" />
              )}
            </>
          ))}
        </CellList>
      </Flex>
    </div>
  )
}
