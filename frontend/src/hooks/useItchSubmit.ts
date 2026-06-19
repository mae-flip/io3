import { useCallback, useMemo, useState } from "react"

import type { ItchGamePublic, SubmitBatchResponse } from "@/client"

const ITCH_ACCESS_TOKEN_KEY = "itch_access_token"
const ITCH_GAMES_KEY = "itch_games"
const ITCH_USERNAME_KEY = "itch_username"
const ITCH_OAUTH_STATE_KEY = "itch_oauth_state"
const ITCH_OAUTH_RETURN_TO_KEY = "oauth_return_to"

function readGames(): ItchGamePublic[] {
  const raw = sessionStorage.getItem(ITCH_GAMES_KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw) as ItchGamePublic[]
  } catch {
    return []
  }
}

export function useItchSubmit() {
  const [games, setGamesState] = useState<ItchGamePublic[]>(() => readGames())
  const [itchUsername, setItchUsername] = useState(
    () => sessionStorage.getItem(ITCH_USERNAME_KEY) ?? "",
  )

  const itchAccessToken = sessionStorage.getItem(ITCH_ACCESS_TOKEN_KEY)
  const hasIo3Token = Boolean(localStorage.getItem("access_token"))
  const isSubmitSessionReady =
    hasIo3Token && Boolean(itchAccessToken) && games.length > 0

  const setSession = useCallback(
    (data: {
      io3Token: string
      itchAccessToken: string
      games: ItchGamePublic[]
      itchUsername: string
    }) => {
      localStorage.setItem("access_token", data.io3Token)
      sessionStorage.setItem(ITCH_ACCESS_TOKEN_KEY, data.itchAccessToken)
      sessionStorage.setItem(ITCH_GAMES_KEY, JSON.stringify(data.games))
      sessionStorage.setItem(ITCH_USERNAME_KEY, data.itchUsername)
      setGamesState(data.games)
      setItchUsername(data.itchUsername)
    },
    [],
  )

  const clearSession = useCallback(() => {
    localStorage.removeItem("access_token")
    sessionStorage.removeItem(ITCH_ACCESS_TOKEN_KEY)
    sessionStorage.removeItem(ITCH_GAMES_KEY)
    sessionStorage.removeItem(ITCH_USERNAME_KEY)
    sessionStorage.removeItem(ITCH_OAUTH_STATE_KEY)
    sessionStorage.removeItem(ITCH_OAUTH_RETURN_TO_KEY)
    setGamesState([])
    setItchUsername("")
  }, [])

  const storeOAuthReturnTo = useCallback((returnTo: string) => {
    sessionStorage.setItem(ITCH_OAUTH_RETURN_TO_KEY, returnTo)
  }, [])

  const consumeOAuthReturnTo = useCallback(() => {
    const returnTo =
      sessionStorage.getItem(ITCH_OAUTH_RETURN_TO_KEY) ?? "/submit"
    sessionStorage.removeItem(ITCH_OAUTH_RETURN_TO_KEY)
    return returnTo
  }, [])

  const storeOAuthState = useCallback((state: string) => {
    sessionStorage.setItem(ITCH_OAUTH_STATE_KEY, state)
  }, [])

  const consumeOAuthState = useCallback(() => {
    const state = sessionStorage.getItem(ITCH_OAUTH_STATE_KEY) ?? ""
    sessionStorage.removeItem(ITCH_OAUTH_STATE_KEY)
    return state
  }, [])

  const selectableGames = useMemo(
    () =>
      games.filter(
        (game) =>
          game.published !== false &&
          game.publicly_viewable !== false &&
          !game.already_indexed &&
          !game.removed_by_moderator,
      ),
    [games],
  )

  return {
    games,
    selectableGames,
    itchUsername,
    itchAccessToken,
    hasIo3Token,
    isSubmitSessionReady,
    setSession,
    clearSession,
    storeOAuthReturnTo,
    consumeOAuthReturnTo,
    storeOAuthState,
    consumeOAuthState,
  }
}

export type { SubmitBatchResponse }
