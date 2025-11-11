import { CellList, Flex, Typography } from '@maxhub/max-ui'
import { useNavigate } from '@tanstack/react-router'
import clsx from 'clsx'
import { Calendar, Plus, Settings, Users } from 'lucide-react'
import { Loader } from '../ui/loader'
import { Role } from '../group/Role'
import { SideBarLink } from './side-bar-link'
import { SideBarSection } from './side-bar-section'
import type { RoleResponse } from '@/lib/api/gen.schemas'
import { routes } from '@/routes'
import { useGroups } from '@/hooks/groups'

export function SideBar({
  isOpen,
  onClose,
}: {
  isOpen: boolean
  onClose: () => void
}) {
  const { data, isPending } = useGroups()
  const navigate = useNavigate()
  const onNavigate = (path: string) => {
    console.log(path)
    navigate({ to: path })
    onClose()
  }

  return (
    <>
      {isOpen && <div onClick={onClose} className="fixed inset-0" />}
      <aside
        className={clsx(
          'z-99 fixed top-0 left-0 h-full w-62 bg-(--background-surface-floating) -translate-x-62 transition-transform',
          {
            'translate-x-0': isOpen,
          },
        )}
      >
        <Flex direction="column" className="h-full">
          <div className="py-4 w-full shrink-0">
            <CellList mode="island" filled>
              {Object.entries(routes)
                .filter(([_, link]) => link.sidebar)
                .map(([path, link]) => (
                  <SideBarLink
                    key={link.title}
                    onClick={() => onNavigate(path)}
                    icon={
                      <link.icon
                        className={clsx({
                          'text-(--accent-themed)': location.pathname === path,
                        })}
                      />
                    }
                    title={link.title}
                    isActive={location.pathname === path}
                  />
                ))}
            </CellList>
          </div>
          <div className="flex-1 overflow-y-auto pb-4 w-full">
            <Flex direction="column" gapY={14} className="w-full">
              {isPending || !data ? (
                <div className="w-full mt-12">
                  <Loader size={24} />
                </div>
              ) : (
                data.groups.map((group) => (
                  <SideBarSection
                    key={group.groupId}
                    title={
                      <Flex gapX={8} align="center">
                        <Typography.Title className="text-sm!">
                          {group.name}
                        </Typography.Title>
                        <Role
                          roleId={
                            group.roleId as unknown as Pick<RoleResponse, 'id'>
                          }
                        />
                      </Flex>
                    }
                  >
                    <SideBarLink
                      title="Расписание"
                      icon={<Calendar />}
                      onClick={() => onNavigate(`/groups/${group.groupId}`)}
                      isActive={
                        location.pathname === `/groups/${group.groupId}`
                      }
                    />
                    <SideBarLink
                      title="Участники"
                      icon={<Users />}
                      onClick={() =>
                        onNavigate(`/groups/${group.groupId}/members`)
                      }
                      isActive={
                        location.pathname === `/groups/${group.groupId}/members`
                      }
                    />
                    {[1].includes(group.roleId) && (
                      <SideBarLink
                        title="Настройки"
                        icon={<Settings />}
                        onClick={() =>
                          onNavigate(`/groups/${group.groupId}/settings`)
                        }
                        isActive={
                          location.pathname ===
                          `/groups/${group.groupId}/settings`
                        }
                      />
                    )}
                  </SideBarSection>
                ))
              )}
              <CellList filled mode="island">
                <SideBarLink
                  title="Создать группу"
                  icon={<Plus />}
                  onClick={() => onNavigate('/groups/create')}
                  isActive={false}
                  showChevron={false}
                />
              </CellList>
            </Flex>
          </div>
        </Flex>
      </aside>
    </>
  )
}
