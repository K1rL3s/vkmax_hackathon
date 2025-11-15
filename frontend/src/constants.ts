import type { Timezone } from './components/timezone-select-modal'

export const PERSONAL_GROUP_NAME = 'Личная'

export const TIMEZONES: Array<Timezone> = [
  {
    label: 'Бейкер и Хауленд (острова, США) −12:00',
    value: -720,
    tz: 'Etc/GMT+12',
  },

  {
    label: 'Американское Самоа, Паго-Паго −11:00',
    value: -660,
    tz: 'Pacific/Pago_Pago',
  },

  {
    label: 'Гавайи (США), Гонолулу −10:00',
    value: -600,
    tz: 'Pacific/Honolulu',
  },

  {
    label: 'Маркизские острова (Французская Полинезия) −09:30',
    value: -570,
    tz: 'Pacific/Marquesas',
  },

  {
    label: 'Аляска (США), Анкоридж −09:00',
    value: -540,
    tz: 'America/Anchorage',
  },

  {
    label: 'Лос-Анджелес, Сиэтл, Ванкувер −08:00',
    value: -480,
    tz: 'America/Los_Angeles',
  },

  {
    label: 'Денвер, Калгари, Эдмонтон −07:00',
    value: -420,
    tz: 'America/Denver',
  },

  {
    label: 'Чикаго, Мехико, Сан-Хосе (Коста-Рика) −06:00',
    value: -360,
    tz: 'America/Chicago',
  },

  {
    label: 'Нью-Йорк, Торонто, Лима, Богота −05:00',
    value: -300,
    tz: 'America/New_York',
  },

  {
    label: 'Сантьяго (Чили), Каракас, Ла-Пас −04:00',
    value: -240,
    tz: 'America/Santiago',
  },

  {
    label: 'Сент-Джонс (Ньюфаундленд, Канада) −03:30',
    value: -210,
    tz: 'America/St_Johns',
  },

  {
    label: 'Буэнос-Айрес, Бразилиа, Монтевидео −03:00',
    value: -180,
    tz: 'America/Argentina/Buenos_Aires',
  },

  { label: 'Лондон, Дублин, Лиссабон ±00:00', value: 0, tz: 'Europe/London' },

  {
    label: 'Париж, Берлин, Рим, Мадрид +01:00',
    value: 60,
    tz: 'Europe/Berlin',
  },

  { label: 'Калининград +02:00', value: 120, tz: 'Europe/Kaliningrad' },

  { label: 'Москва, Санкт-Петербург +03:00', value: 180, tz: 'Europe/Moscow' },

  { label: 'Екатеринбург +05:00', value: 300, tz: 'Asia/Yekaterinburg' },
]

export const ADMIN_ROLE_ID = 1
export const SUPERVISOR_ROLE_ID = 2
export const MEMBER_ROLE_ID = 3
