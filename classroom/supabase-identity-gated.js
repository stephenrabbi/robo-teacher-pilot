/* Robo-Teacher Supabase identity adapter — intentionally NOT loaded by the live classroom.
 * Feature gate stays off until privacy, guardian and two-account isolation tests pass.
 * A nickname or IND-/school code is NOT proof of identity.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==="object" && module.exports)module.exports=api;
  else root.RoboSupabaseIdentity=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const ENABLED=false;
  function createAdapter(supabase,options={}){
    if(!supabase || !supabase.auth || typeof supabase.auth.getUser!=="function")throw new TypeError("Supabase auth client required");
    const enabled=ENABLED && options.enabled===true;
    async function verifiedUser(){
      if(!enabled)return null;
      const {data,error}=await supabase.auth.getUser();
      if(error)throw error;
      return data?.user?.id ? data.user : null;
    }
    async function readOwnProgress(){
      const user=await verifiedUser();
      if(!user)return {enabled:false,rows:[]};
      const {data,error}=await supabase.from("robo_learning_progress")
        .select("topic_code,mastery_score,updated_at")
        .eq("user_id",user.id).limit(100);
      if(error)throw error;
      return {enabled:true,rows:data||[]};
    }
    async function readOwnProfile(){
      const user=await verifiedUser();
      if(!user)return {enabled:false,profile:null};
      const {data,error}=await supabase.from("robo_learner_profiles")
        .select("user_id,school_id,created_at").eq("user_id",user.id).maybeSingle();
      if(error)throw error;
      return {enabled:true,profile:data||null};
    }
    return Object.freeze({enabled,verifiedUser,readOwnProgress,readOwnProfile});
  }
  return Object.freeze({ENABLED,createAdapter});
});
